import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CORE_SEARCH_DIRS, SYSTEM_BLACKLIST_DIRS, EXT_MAP

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class FileCandidate:
    def __init__(self, path: Path, score: float = 0.0, match_reason: str = ""):
        self.path = path
        self.filename = path.name
        self.extension = path.suffix.lower()
        self.size_bytes = path.stat().st_size if path.exists() else 0
        self.mtime = datetime.fromtimestamp(path.stat().st_mtime) if path.exists() else datetime.min
        self.score = score
        self.match_reason = match_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.filename,
            "path": str(self.path),
            "size_kb": round(self.size_bytes / 1024, 1),
            "modified": self.mtime.strftime("%Y-%m-%d %H:%M"),
            "score": round(self.score, 2),
            "reason": self.match_reason
        }


def parse_date_window(date_hint: Optional[str]) -> Optional[datetime]:
    """Converts natural language date hints into a threshold datetime."""
    if not date_hint:
        return None
    now = datetime.now()
    dh = date_hint.lower()
    
    if "today" in dh or "aaj" in dh:
        return now - timedelta(days=1)
    elif "yesterday" in dh or "kal" in dh:
        return now - timedelta(days=2)
    elif "this week" in dh or "is hafte" in dh:
        return now - timedelta(days=7)
    elif "last week" in dh or "pichle hafte" in dh:
        return now - timedelta(days=14)
    elif "this month" in dh or "is mahine" in dh:
        return now - timedelta(days=30)
    elif "last month" in dh or "pichle mahine" in dh:
        return now - timedelta(days=60)
    
    # Check for "X days"
    for word in dh.split():
        if word.isdigit():
            return now - timedelta(days=int(word))
    return None


def calculate_string_similarity(s1: str, s2: str) -> float:
    """Calculates similarity between query and filename."""
    s1, s2 = s1.lower(), s2.lower()
    if HAS_RAPIDFUZZ:
        # Weighted combination of partial and token sort ratio
        partial = fuzz.partial_ratio(s1, s2)
        token_sort = fuzz.token_sort_ratio(s1, s2)
        return max(partial, token_sort)
    else:
        # Fallback simple substring / set overlap
        if s1 in s2 or s2 in s1:
            return 85.0
        words1 = set(s1.split())
        words2 = set(s2.split())
        overlap = words1.intersection(words2)
        return (len(overlap) / max(len(words1), 1)) * 70.0


def extract_content_snippet(file_path: Path, max_chars: int = 15000) -> str:
    """Safely extracts plain text from PDF, DOCX, TXT, CSV, MD files."""
    ext = file_path.suffix.lower()
    text = ""
    try:
        if ext in {".txt", ".md", ".csv", ".json", ".py", ".log", ".html"}:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read(max_chars)
            except Exception:
                with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                    text = f.read(max_chars)

        elif ext == ".pdf" and HAS_PYPDF:
            reader = pypdf.PdfReader(str(file_path))
            # Extract first 5 pages max to keep search blazing fast
            pages = min(5, len(reader.pages))
            for i in range(pages):
                page_text = reader.pages[i].extract_text() or ""
                text += page_text + "\n"
                if len(text) >= max_chars:
                    break

        elif ext == ".docx" and HAS_DOCX:
            doc = docx.Document(str(file_path))
            for p in doc.paragraphs:
                text += p.text + "\n"
                if len(text) >= max_chars:
                    break
    except Exception:
        pass
    return text


def scan_file_system(
    query: str,
    file_type: Optional[str] = None,
    date_range: Optional[str] = None,
    content_hint: Optional[str] = None,
    max_results: int = 5,
    max_depth: int = 3
) -> List[Dict[str, Any]]:
    """
    Core 4-Tier Smart File Resolver.
    Finds files even if name or exact directory is unknown.
    """
    threshold_date = parse_date_window(date_range)
    allowed_extensions = EXT_MAP.get(file_type.lower()) if file_type else None
    
    query_tokens = [q.lower() for q in query.split() if len(q) > 2]
    candidates: List[FileCandidate] = []
    
    for base_dir in CORE_SEARCH_DIRS:
        if not base_dir.exists():
            continue
            
        for root, dirs, files in os.walk(base_dir):
            # Prune blacklisted folders to maintain fast speed
            dirs[:] = [d for d in dirs if d not in SYSTEM_BLACKLIST_DIRS and not d.startswith(".")]
            
            # Check depth limit
            depth = len(Path(root).relative_to(base_dir).parts)
            if depth > max_depth:
                dirs.clear()
                continue
                
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                # Filter 1: File type / extension check
                if allowed_extensions and ext not in allowed_extensions:
                    continue
                    
                try:
                    stat = file_path.stat()
                    file_mtime = datetime.fromtimestamp(stat.st_mtime)
                except (OSError, PermissionError):
                    continue
                    
                # Filter 2: Date window filter
                if threshold_date and file_mtime < threshold_date:
                    continue
                    
                # Tier 2: Fuzzy filename matching
                name_sim = calculate_string_similarity(query, file)
                score = name_sim
                match_reasons = []
                
                if name_sim >= 60:
                    match_reasons.append(f"Filename matches query ({int(name_sim)}% similarity)")
                
                # Recency bonus (files modified in last 7 days get boost)
                days_old = (datetime.now() - file_mtime).days
                if days_old <= 7:
                    score += 15
                    match_reasons.append(f"Recently modified ({days_old}d ago)")
                elif days_old <= 30:
                    score += 5
                    
                # Tier 3: Content inspection (if query or content_hint provided)
                check_content = content_hint or (score < 70 and ext in {".pdf", ".docx", ".txt", ".md", ".csv"})
                if check_content:
                    snippet = extract_content_snippet(file_path).lower()
                    if snippet:
                        search_target = (content_hint or query).lower()
                        target_words = search_target.split()
                        matched_words = [w for w in target_words if len(w) > 2 and w in snippet]
                        if matched_words:
                            content_boost = min(40, len(matched_words) * 15)
                            score += content_boost
                            match_reasons.append(f"Contains matching text inside: '{', '.join(matched_words)}'")
                
                if score >= 45:
                    candidate = FileCandidate(
                        path=file_path,
                        score=score,
                        match_reason="; ".join(match_reasons) or "Metadata matched"
                    )
                    candidates.append(candidate)

    # Sort descending by score
    candidates.sort(key=lambda c: c.score, reverse=True)
    return [c.to_dict() for c in candidates[:max_results]]
