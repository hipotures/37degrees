"""
Citation database management for research references
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from contextlib import contextmanager

from rich.console import Console

console = Console()


class CitationDatabase:
    """Manage citations in SQLite database for each book"""
    
    def __init__(self, book_path: Path):
        """Initialize citation database for a book
        
        Args:
            book_path: Path to book.yaml file
        """
        self.book_dir = book_path.parent
        self.db_path = self.book_dir / 'book.db'
        self.create_tables()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Citations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    date TEXT,
                    last_updated TEXT,
                    provider TEXT NOT NULL,
                    topic TEXT,
                    relevance_score REAL,
                    added_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    accessed_at TEXT,
                    domain TEXT,
                    language TEXT DEFAULT 'pl',
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(provider, url)
                )
            """)
            
            # Research sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    book_title TEXT,
                    author TEXT,
                    topics_researched TEXT,
                    total_citations INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Citation usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citation_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    citation_id INTEGER NOT NULL,
                    session_id INTEGER,
                    context TEXT,
                    position INTEGER,
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (citation_id) REFERENCES citations(id),
                    FOREIGN KEY (session_id) REFERENCES research_sessions(id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_citations_provider ON citations(provider)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_citations_topic ON citations(topic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_citations_domain ON citations(domain)")
            
            conn.commit()
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def add_citation(self, url: str, title: str = None, date: str = None,
                    last_updated: str = None, provider: str = "unknown",
                    topic: str = None, relevance_score: float = None) -> int:
        """Add a citation to the database
        
        Args:
            url: Citation URL
            title: Page/article title
            date: Original publication date
            last_updated: Last update date
            provider: Research provider (perplexity, google, etc.)
            topic: Research topic category
            relevance_score: Relevance score (0-1)
            
        Returns:
            Citation ID
        """
        domain = self.extract_domain(url)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Try to insert new citation
                cursor.execute("""
                    INSERT INTO citations 
                    (url, title, date, last_updated, provider, topic, 
                     relevance_score, domain, accessed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (url, title, date, last_updated, provider, topic,
                     relevance_score, domain))
                
                conn.commit()
                return cursor.lastrowid
                
            except sqlite3.IntegrityError:
                # Citation already exists, get its ID
                cursor.execute("""
                    SELECT id FROM citations 
                    WHERE provider = ? AND url = ?
                """, (provider, url))
                
                result = cursor.fetchone()
                if result:
                    # Update accessed_at
                    cursor.execute("""
                        UPDATE citations 
                        SET accessed_at = datetime('now', 'localtime')
                        WHERE id = ?
                    """, (result['id'],))
                    conn.commit()
                    return result['id']
                else:
                    raise Exception(f"Failed to add citation: {url}")
    
    def get_citation_id(self, url: str, provider: str) -> Optional[int]:
        """Get citation ID if exists
        
        Args:
            url: Citation URL
            provider: Research provider
            
        Returns:
            Citation ID or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM citations 
                WHERE provider = ? AND url = ?
            """, (provider, url))
            
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def create_research_session(self, provider: str, book_title: str,
                              author: str, topics: List[str],
                              metadata: Dict[str, Any] = None) -> int:
        """Create a new research session
        
        Args:
            provider: Research provider
            book_title: Book title
            author: Book author
            topics: List of topics researched
            metadata: Additional metadata
            
        Returns:
            Session ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO research_sessions 
                (provider, book_title, author, topics_researched, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (provider, book_title, author, json.dumps(topics),
                 json.dumps(metadata or {})))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_session_citations(self, session_id: int, count: int):
        """Update total citations for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE research_sessions 
                SET total_citations = ?
                WHERE id = ?
            """, (count, session_id))
            conn.commit()
    
    def add_citation_usage(self, citation_id: int, session_id: int = None,
                          context: str = None, position: int = None):
        """Track where a citation is used
        
        Args:
            citation_id: Citation ID
            session_id: Research session ID
            context: Surrounding text
            position: Character position in content
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO citation_usage 
                (citation_id, session_id, context, position)
                VALUES (?, ?, ?, ?)
            """, (citation_id, session_id, context, position))
            
            conn.commit()
    
    def get_citations_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all citations for a topic"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM citations 
                WHERE topic = ? AND is_active = 1
                ORDER BY relevance_score DESC, added_at DESC
            """, (topic,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_citations(self) -> List[Dict[str, Any]]:
        """Get all active citations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM citations 
                WHERE is_active = 1
                ORDER BY id
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_citation_by_id(self, citation_id: int) -> Optional[Dict[str, Any]]:
        """Get citation by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM citations 
                WHERE id = ?
            """, (citation_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def export_citations(self, format: str = "markdown") -> str:
        """Export citations in various formats
        
        Args:
            format: Export format (markdown, bibtex, json)
            
        Returns:
            Formatted citations
        """
        citations = self.get_all_citations()
        
        if format == "markdown":
            lines = ["### 📚 Bibliografia\n"]
            for citation in citations:
                title = citation['title'] or citation['domain']
                date = f" ({citation['date']})" if citation['date'] else ""
                lines.append(f"[{citation['id']}] {citation['url']} - \"{title}\"{date}")
            return "\n".join(lines)
            
        elif format == "json":
            return json.dumps(citations, indent=2, ensure_ascii=False)
            
        elif format == "bibtex":
            lines = []
            for citation in citations:
                entry_type = "@misc"
                cite_key = f"citation{citation['id']}"
                title = citation['title'] or f"Online resource from {citation['domain']}"
                
                lines.append(f"{entry_type}{{{cite_key},")
                lines.append(f"  title = {{{title}}},")
                lines.append(f"  url = {{{citation['url']}}},")
                if citation['date']:
                    lines.append(f"  year = {{{citation['date'][:4]}}},")
                lines.append(f"  note = {{Accessed: {citation['accessed_at']}}}")
                lines.append("}\n")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_citation_stats(self) -> Dict[str, Any]:
        """Get citation statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total citations
            cursor.execute("SELECT COUNT(*) as total FROM citations")
            total = cursor.fetchone()['total']
            
            # By provider
            cursor.execute("""
                SELECT provider, COUNT(*) as count 
                FROM citations 
                GROUP BY provider
            """)
            by_provider = {row['provider']: row['count'] for row in cursor.fetchall()}
            
            # By topic
            cursor.execute("""
                SELECT topic, COUNT(*) as count 
                FROM citations 
                WHERE topic IS NOT NULL
                GROUP BY topic
            """)
            by_topic = {row['topic']: row['count'] for row in cursor.fetchall()}
            
            # Top domains
            cursor.execute("""
                SELECT domain, COUNT(*) as count 
                FROM citations 
                WHERE domain IS NOT NULL
                GROUP BY domain
                ORDER BY count DESC
                LIMIT 10
            """)
            top_domains = [(row['domain'], row['count']) for row in cursor.fetchall()]
            
            return {
                'total': total,
                'by_provider': by_provider,
                'by_topic': by_topic,
                'top_domains': top_domains
            }