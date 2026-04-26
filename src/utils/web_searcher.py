"""
Web search integration for multi-source knowledge pipeline.
Provides access to .edu.br portals, arXiv, and Semantic Scholar APIs.
"""
import requests
import xml.etree.ElementTree as ET
from typing import Optional


class WebSearcher:
    """Searchable web sources: Brazilian academic portals, arXiv, and Semantic Scholar."""

    ARXIV_API = "https://export.arxiv.org/api/query"
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

    MAX_RESULTS = 3
    TIMEOUT = 10

    @staticmethod
    def search_edu_br(topic: str, max_results: int = 3) -> str:
        """
        Search Brazilian academic portals (.edu.br) for relevant materials.
        Uses DuckDuckGo to search across .edu.br domain.
        """
        try:
            from duckduckgo_search import DDGS

            # Build search query with domain filter and keywords
            query = f"{topic} site:.edu.br (pdf OR repositório OR biblioteca OR portal)"

            results = []
            with DDGS(timeout=WebSearcher.TIMEOUT) as ddg:
                for r in ddg.text(query, max_results=max_results):
                    title = r.get("title", "Sem título")
                    body = (r.get("body", "")[:250]).strip()
                    href = r.get("href", "")

                    if title and href:
                        results.append(f"• **{title}**\n  {body}\n  🔗 {href}")

            return "\n\n".join(results) if results else ""

        except ImportError:
            print("[edu.br] duckduckgo-search not available")
            return ""
        except Exception as e:
            print(f"[edu.br Search] Error: {e}")
            return ""

    @staticmethod
    def search_arxiv(topic: str, max_results: int = 3) -> str:
        """
        Search arXiv for open-access research papers.
        Queries title and abstract fields.
        """
        try:
            # arXiv API doesn't require authentication
            response = requests.get(
                WebSearcher.ARXIV_API,
                params={
                    "search_query": f"ti:{topic} OR abs:{topic}",
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending"
                },
                timeout=WebSearcher.TIMEOUT
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            results = []
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                published_elem = entry.find("atom:published", ns)

                if title_elem is not None and summary_elem is not None:
                    title = title_elem.text.strip()
                    summary = summary_elem.text.strip()[:300]
                    year = published_elem.text[:4] if published_elem is not None else "N/A"

                    results.append(f"• **{title}** ({year})\n  {summary}...")

            return "\n\n".join(results) if results else ""

        except Exception as e:
            print(f"[arXiv] Error: {e}")
            return ""

    @staticmethod
    def search_semantic_scholar(topic: str, max_results: int = 3) -> str:
        """
        Search Semantic Scholar for papers and citations.
        Open API without authentication required.
        """
        try:
            response = requests.get(
                WebSearcher.SEMANTIC_SCHOLAR_API,
                params={
                    "query": topic,
                    "fields": "title,abstract,year,authors,venue",
                    "limit": max_results
                },
                timeout=WebSearcher.TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for paper in data.get("data", []):
                title = paper.get("title", "")
                abstract = paper.get("abstract", "") or ""
                year = paper.get("year", "")
                venue = paper.get("venue", "") or "Open access"

                if title:
                    abstract_preview = abstract[:300] if abstract else "Sem resumo disponível"
                    results.append(f"• **{title}** ({year})\n  Veículo: {venue}\n  {abstract_preview}...")

            return "\n\n".join(results) if results else ""

        except Exception as e:
            print(f"[Semantic Scholar] Error: {e}")
            return ""

    @staticmethod
    def search_all(topic: str) -> tuple[str, str, str]:
        """
        Perform all three web searches in parallel (conceptually).
        Returns (edu_br_results, arxiv_results, scholar_results).
        """
        edu_br = WebSearcher.search_edu_br(topic, WebSearcher.MAX_RESULTS)
        arxiv = WebSearcher.search_arxiv(topic, WebSearcher.MAX_RESULTS)
        scholar = WebSearcher.search_semantic_scholar(topic, WebSearcher.MAX_RESULTS)
        return edu_br, arxiv, scholar
