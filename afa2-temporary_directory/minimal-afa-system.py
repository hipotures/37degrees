#!/usr/bin/env python3
"""
Minimal AFA (Audio Format Analysis) System
Uproszczony system wyboru formatów audio dla adaptacji książek
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
from datetime import datetime

# =================== KONFIGURACJA ===================

FORMATS = {
    1: {
        "name": "Dialog eksploracyjny",
        "hosts": ("Entuzjasta", "Sceptyk"),
        "base_duration": 10,
        "weights": {"impact": 1.2, "relevance": 1.1}
    },
    2: {
        "name": "Debata krytyczna", 
        "hosts": ("Adwokat", "Krytyk"),
        "base_duration": 12,
        "weights": {"controversy": 1.5, "complexity": 1.2}
    },
    3: {
        "name": "Analiza akademicka",
        "hosts": ("Profesor", "Student"),
        "base_duration": 14,
        "weights": {"complexity": 1.4, "impact": 1.1}
    },
    4: {
        "name": "Rekonstrukcja narracyjna",
        "hosts": ("Reporter", "Świadek"),
        "base_duration": 11,
        "weights": {"complexity": 1.3, "controversy": 1.1}
    },
    5: {
        "name": "Kontekst czasowy",
        "hosts": ("Współczesny", "Klasyk"),
        "base_duration": 12,
        "weights": {"relevance": 1.4, "impact": 1.2}
    },
    6: {
        "name": "Perspektywa emocjonalna",
        "hosts": ("Emocja", "Analiza"),
        "base_duration": 11,
        "weights": {"complexity": 1.2, "relevance": 1.1}
    },
    7: {
        "name": "Wymiar kulturowy",
        "hosts": ("Lokalny", "Globalny"),
        "base_duration": 10,
        "weights": {"impact": 1.3, "relevance": 1.2}
    },
    8: {
        "name": "Perspektywa społeczna",
        "hosts": ("Socjolog", "Historyk"),
        "base_duration": 13,
        "weights": {"controversy": 1.3, "impact": 1.2}
    }
}

# =================== STRUKTURY DANYCH ===================

@dataclass
class BookScores:
    """Uproszczone wymiary oceny książki (0-10)"""
    complexity: float = 0    # Złożoność narracyjna
    impact: float = 0        # Wpływ kulturowy
    controversy: float = 0   # Kontrowersyjność
    relevance: float = 0     # Aktualność tematyki
    
    @property
    def total(self) -> float:
        return self.complexity + self.impact + self.controversy + self.relevance

@dataclass
class FormatChoice:
    """Wybrany format z uzasadnieniem"""
    format_id: int
    name: str
    duration: int
    score: float
    reason: str

@dataclass 
class AFADocument:
    """Dokument wyjściowy AFA"""
    book_id: str
    title: str
    scores: BookScores
    format: FormatChoice
    prompts: Dict[str, str]
    structure: List[str]
    metadata: Dict = field(default_factory=dict)

# =================== GŁÓWNY AGENT AFA ===================

class MinimalAFAAgent:
    """Minimalny agent do analizy i wyboru formatu audio"""
    
    def __init__(self, history_size: int = 12):
        self.history = deque(maxlen=history_size)
        self.cooldown = 2
        
    def evaluate_book(self, book_data: Dict) -> BookScores:
        """Ocenia książkę w 4 wymiarach"""
        scores = BookScores()
        
        # Uproszczona logika punktacji
        if book_data.get('year', 2000) < 1900:
            scores.complexity += 3
            scores.impact += 2
            
        if book_data.get('translations', 0) > 50:
            scores.impact += 4
            
        if 'controversy' in book_data.get('tags', []):
            scores.controversy += 5
            
        if book_data.get('adaptations', 0) > 3:
            scores.relevance += 3
            scores.impact += 2
            
        # Normalizacja do skali 0-10
        for field in ['complexity', 'impact', 'controversy', 'relevance']:
            value = getattr(scores, field)
            setattr(scores, field, min(10, value))
            
        return scores
    
    def calculate_format_affinity(self, scores: BookScores, format_id: int) -> float:
        """Oblicza dopasowanie książki do formatu"""
        format_config = FORMATS[format_id]
        weights = format_config['weights']
        
        affinity = 0
        for dimension, weight in weights.items():
            score_value = getattr(scores, dimension, 0)
            affinity += score_value * weight
            
        # Kara za niedawne użycie
        recent_uses = sum(1 for f in list(self.history)[-self.cooldown:] if f == format_id)
        if recent_uses > 0:
            affinity *= 0.5
            
        return affinity
    
    def select_format(self, scores: BookScores, book_id: str) -> FormatChoice:
        """Wybiera najlepszy format dla książki"""
        
        # Oblicz dopasowanie dla każdego formatu
        affinities = {}
        for format_id in FORMATS:
            affinities[format_id] = self.calculate_format_affinity(scores, format_id)
        
        # Wybierz format z najwyższym dopasowaniem
        best_format = max(affinities, key=affinities.get)
        
        # Deterministyczny tie-breaker przez hash
        if len([v for v in affinities.values() if v == affinities[best_format]]) > 1:
            hash_val = int(hashlib.md5(book_id.encode()).hexdigest(), 16)
            candidates = [k for k, v in affinities.items() if v == affinities[best_format]]
            best_format = candidates[hash_val % len(candidates)]
        
        # Oblicz długość
        base_duration = FORMATS[best_format]['base_duration']
        duration = min(15, base_duration + int(scores.complexity * 0.3))
        
        # Dodaj do historii
        self.history.append(best_format)
        
        return FormatChoice(
            format_id=best_format,
            name=FORMATS[best_format]['name'],
            duration=duration,
            score=affinities[best_format],
            reason=f"Najlepsze dopasowanie: {affinities[best_format]:.2f} (complexity={scores.complexity:.1f})"
        )
    
    def generate_prompts(self, format_choice: FormatChoice, book_title: str) -> Dict[str, str]:
        """Generuje prompty dla wybranego formatu"""
        format_config = FORMATS[format_choice.format_id]
        host_a, host_b = format_config['hosts']
        
        prompts = {
            "Host_A": f"Jesteś {host_a}. Omawiasz '{book_title}' z perspektywy "
                     f"swojej roli w formacie '{format_choice.name}'. "
                     f"Mów naturalnie, 3-4 zdania na wypowiedź.",
            
            "Host_B": f"Jesteś {host_b}. Dopełniasz perspektywę {host_a} "
                     f"w dyskusji o '{book_title}'. Zadawaj pytania, "
                     f"rozwijaj wątki, zachowuj dynamikę rozmowy."
        }
        
        return prompts
    
    def generate_structure(self, format_choice: FormatChoice, scores: BookScores) -> List[str]:
        """Generuje strukturę odcinka"""
        duration = format_choice.duration
        
        structure = [
            f"[0:00-2:00] Wprowadzenie - przedstawienie książki i formatu",
            f"[2:00-{duration//2}:00] Główna dyskusja - kluczowe tematy",
            f"[{duration//2}:00-{duration-2}:00] Pogłębienie - kontrowersje i konteksty",
            f"[{duration-2}:00-{duration}:00] Podsumowanie - wnioski i rekomendacje"
        ]
        
        return structure
    
    def process_book(self, book_data: Dict) -> AFADocument:
        """Główny proces przetwarzania książki"""
        
        # 1. Oceń książkę
        scores = self.evaluate_book(book_data)
        
        # 2. Wybierz format
        format_choice = self.select_format(scores, book_data['id'])
        
        # 3. Wygeneruj prompty
        prompts = self.generate_prompts(format_choice, book_data['title'])
        
        # 4. Wygeneruj strukturę
        structure = self.generate_structure(format_choice, scores)
        
        # 5. Złóż dokument
        return AFADocument(
            book_id=book_data['id'],
            title=book_data['title'],
            scores=scores,
            format=format_choice,
            prompts=prompts,
            structure=structure,
            metadata={
                'processed_at': datetime.now().isoformat(),
                'agent_version': '1.0-minimal'
            }
        )
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki użycia formatów"""
        from collections import Counter
        
        format_counts = Counter(self.history)
        total = len(self.history)
        
        stats = {
            'total_processed': total,
            'format_distribution': {}
        }
        
        for format_id, count in format_counts.items():
            stats['format_distribution'][FORMATS[format_id]['name']] = {
                'count': count,
                'percentage': round(100 * count / total, 1) if total > 0 else 0
            }
            
        return stats

# =================== FUNKCJE POMOCNICZE ===================

def export_afa_document(doc: AFADocument, format: str = 'json') -> str:
    """Eksportuje dokument AFA do wybranego formatu"""
    
    if format == 'json':
        return json.dumps({
            'book_id': doc.book_id,
            'title': doc.title,
            'scores': {
                'complexity': doc.scores.complexity,
                'impact': doc.scores.impact,
                'controversy': doc.scores.controversy,
                'relevance': doc.scores.relevance,
                'total': doc.scores.total
            },
            'format': {
                'id': doc.format.format_id,
                'name': doc.format.name,
                'duration': doc.format.duration,
                'score': doc.format.score,
                'reason': doc.format.reason
            },
            'prompts': doc.prompts,
            'structure': doc.structure,
            'metadata': doc.metadata
        }, indent=2)
    
    elif format == 'markdown':
        md = f"""# AFA: {doc.title}

## Scores
- Complexity: {doc.scores.complexity}/10
- Impact: {doc.scores.impact}/10  
- Controversy: {doc.scores.controversy}/10
- Relevance: {doc.scores.relevance}/10
- **Total: {doc.scores.total}/40**

## Format
- **{doc.format.name}** ({doc.format.duration} min)
- Reason: {doc.format.reason}

## Prompts
### Host A
{doc.prompts['Host_A']}

### Host B  
{doc.prompts['Host_B']}

## Structure
"""
        for segment in doc.structure:
            md += f"- {segment}\n"
        
        return md
    
    else:
        raise ValueError(f"Unsupported format: {format}")

# =================== PRZYKŁAD UŻYCIA ===================

def main():
    """Przykład użycia minimalnego systemu AFA"""
    
    # Inicjalizacja agenta
    agent = MinimalAFAAgent(history_size=12)
    
    # Przykładowe dane książek
    books = [
        {
            'id': '0001_alice',
            'title': 'Alice in Wonderland',
            'year': 1865,
            'translations': 174,
            'adaptations': 20,
            'tags': ['classic', 'fantasy']
        },
        {
            'id': '0094_invisible',
            'title': 'The Invisible Man',
            'year': 1897,
            'translations': 100,
            'adaptations': 60,
            'tags': ['sci-fi', 'controversy', 'classic']
        },
        {
            'id': '0042_1984',
            'title': '1984',
            'year': 1949,
            'translations': 65,
            'adaptations': 5,
            'tags': ['dystopia', 'controversy', 'political']
        }
    ]
    
    # Przetwórz książki
    results = []
    for book in books:
        doc = agent.process_book(book)
        results.append(doc)
        
        print(f"\n{'='*50}")
        print(f"Processed: {doc.title}")
        print(f"Format: {doc.format.name} ({doc.format.duration} min)")
        print(f"Scores: C={doc.scores.complexity:.1f} I={doc.scores.impact:.1f} "
              f"Co={doc.scores.controversy:.1f} R={doc.scores.relevance:.1f}")
    
    # Pokaż statystyki
    print(f"\n{'='*50}")
    print("STATISTICS:")
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Eksportuj przykładowy dokument
    print(f"\n{'='*50}")
    print("EXAMPLE EXPORT (Markdown):")
    print(export_afa_document(results[0], 'markdown'))

if __name__ == '__main__':
    main()