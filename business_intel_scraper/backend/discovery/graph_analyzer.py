"""
Crawl Graph Analyzer using NetworkX for Business Intelligence Discovery

This module provides graph-based analysis of crawl patterns to optimize
discovery strategies and identify high-value target clusters.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter
import json
from pathlib import Path

try:
    import networkx as nx
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

logger = logging.getLogger(__name__)


class CrawlGraphAnalyzer:
    """
    NetworkX-based analyzer for crawl graph patterns and optimization.

    Features:
    - Graph construction from crawl data
    - Centrality analysis for important nodes
    - Community detection for target clustering
    - Path optimization for efficient crawling
    - Value propagation through link relationships
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.graph: Optional[Any] = nx.DiGraph() if NETWORKX_AVAILABLE else None
        self.value_cache: Dict[str, float] = {}
        self.analysis_cache: Dict[str, Any] = {}
        self.last_analysis: Optional[float] = None

        # Configuration
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        self.min_nodes_for_analysis = self.config.get("min_nodes_for_analysis", 50)
        self.max_nodes_display = self.config.get("max_nodes_display", 1000)

        logger.info(
            f"CrawlGraphAnalyzer initialized with NetworkX support: {NETWORKX_AVAILABLE}"
        )

        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available, graph analysis disabled")

    def add_crawl_result(
        self,
        url: str,
        parent_url: Optional[str] = None,
        extracted_links: Optional[List[str]] = None,
        success: bool = True,
        data_value: float = 0.0,
        response_time: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a crawl result to the graph"""
        if not self.graph:
            return

        try:
            # Add node with attributes
            node_attrs = {
                "success": success,
                "data_value": data_value,
                "response_time": response_time,
                "crawled_at": time.time(),
                "extracted_links_count": len(extracted_links) if extracted_links else 0,
            }

            if metadata:
                node_attrs.update(metadata)

            self.graph.add_node(url, **node_attrs)

            # Add edge from parent if specified
            if parent_url and parent_url != url:
                self.graph.add_edge(
                    parent_url, url, discovered_at=time.time(), success=success
                )

            # Add edges to extracted links
            if extracted_links:
                for link in extracted_links:
                    if link != url:  # avoid self-loops
                        self.graph.add_edge(
                            url, link, extracted=True, discovered_at=time.time()
                        )

            # Clear analysis cache
            self.analysis_cache.clear()

            logger.debug(f"Added crawl result to graph: {url} (success: {success})")

        except Exception as e:
            logger.error(f"Failed to add crawl result to graph: {e}")

    def analyze_crawl_patterns(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Analyze crawl patterns and return comprehensive insights"""
        if not self.graph or len(self.graph.nodes()) < self.min_nodes_for_analysis:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.min_nodes_for_analysis} nodes for analysis",
                "nodes": len(self.graph.nodes()) if self.graph else 0,
            }

        # Check cache
        if (
            not force_refresh
            and self.last_analysis
            and time.time() - self.last_analysis < self.cache_ttl
            and self.analysis_cache
        ):
            return self.analysis_cache

        try:
            analysis = {
                "timestamp": time.time(),
                "graph_stats": self._get_graph_statistics(),
                "centrality_analysis": self._analyze_centrality(),
                "community_detection": self._detect_communities(),
                "value_propagation": self._analyze_value_propagation(),
                "crawl_efficiency": self._analyze_crawl_efficiency(),
                "recommendations": self._generate_recommendations(),
            }

            # Cache results
            self.analysis_cache = analysis
            self.last_analysis = time.time()

            return analysis

        except Exception as e:
            logger.error(f"Graph analysis failed: {e}")
            return {"status": "error", "message": str(e)}

    def _get_graph_statistics(self) -> Dict[str, Any]:
        """Calculate basic graph statistics"""
        if not self.graph:
            return {}

        nodes = list(self.graph.nodes())
        edges = list(self.graph.edges())

        # Basic metrics
        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph),
        }

        # Success metrics
        successful_nodes = [
            n for n in nodes if self.graph.nodes[n].get("success", False)
        ]
        stats.update(
            {
                "successful_crawls": len(successful_nodes),
                "success_rate": len(successful_nodes) / len(nodes) if nodes else 0.0,
            }
        )

        # Value metrics
        node_values = [self.graph.nodes[n].get("data_value", 0.0) for n in nodes]
        if node_values:
            stats.update(
                {
                    "avg_data_value": np.mean(node_values),
                    "total_data_value": np.sum(node_values),
                    "max_data_value": np.max(node_values),
                }
            )

        # Response time metrics
        response_times = [
            self.graph.nodes[n].get("response_time", 0.0)
            for n in nodes
            if self.graph.nodes[n].get("response_time", 0.0) > 0
        ]
        if response_times:
            stats.update(
                {
                    "avg_response_time": np.mean(response_times),
                    "median_response_time": np.median(response_times),
                }
            )

        return stats

    def _analyze_centrality(self) -> Dict[str, Any]:
        """Analyze node centrality to identify important URLs"""
        if not self.graph:
            return {}

        try:
            # Calculate different centrality measures
            pagerank = nx.pagerank(self.graph, weight="data_value")
            in_degree = dict(self.graph.in_degree())
            out_degree = dict(self.graph.out_degree())

            # Combine centrality with success metrics
            centrality_scores = {}
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                success = node_data.get("success", False)
                data_value = node_data.get("data_value", 0.0)

                centrality_scores[node] = {
                    "pagerank": pagerank.get(node, 0.0),
                    "in_degree": in_degree.get(node, 0),
                    "out_degree": out_degree.get(node, 0),
                    "success": success,
                    "data_value": data_value,
                    "composite_score": (
                        pagerank.get(node, 0.0) * 0.4
                        + (data_value * 0.3)
                        + (1.0 if success else 0.0) * 0.3
                    ),
                }

            # Top nodes by different metrics
            top_pagerank = sorted(
                centrality_scores.items(), key=lambda x: x[1]["pagerank"], reverse=True
            )[:10]

            top_composite = sorted(
                centrality_scores.items(),
                key=lambda x: x[1]["composite_score"],
                reverse=True,
            )[:10]

            return {
                "top_pagerank_nodes": [
                    (url, scores["pagerank"]) for url, scores in top_pagerank
                ],
                "top_composite_nodes": [
                    (url, scores["composite_score"]) for url, scores in top_composite
                ],
                "avg_pagerank": np.mean(list(pagerank.values())),
                "centrality_distribution": self._get_centrality_distribution(pagerank),
            }

        except Exception as e:
            logger.error(f"Centrality analysis failed: {e}")
            return {}

    def _detect_communities(self) -> Dict[str, Any]:
        """Detect communities in the crawl graph"""
        if not self.graph or len(self.graph.nodes()) < 10:
            return {}

        try:
            # Convert to undirected for community detection
            undirected = self.graph.to_undirected()

            # Use Louvain method for community detection
            import networkx.algorithms.community as nx_comm

            communities = list(nx_comm.greedy_modularity_communities(undirected))

            # Analyze communities
            community_analysis = []
            for i, community in enumerate(communities):
                community_nodes = list(community)

                # Calculate community metrics
                successful_nodes = sum(
                    1
                    for n in community_nodes
                    if self.graph.nodes[n].get("success", False)
                )
                total_value = sum(
                    self.graph.nodes[n].get("data_value", 0.0) for n in community_nodes
                )

                community_analysis.append(
                    {
                        "community_id": i,
                        "size": len(community_nodes),
                        "success_rate": (
                            successful_nodes / len(community_nodes)
                            if community_nodes
                            else 0.0
                        ),
                        "total_value": total_value,
                        "avg_value": (
                            total_value / len(community_nodes)
                            if community_nodes
                            else 0.0
                        ),
                        "sample_nodes": community_nodes[:5],  # sample nodes
                    }
                )

            # Sort by total value
            community_analysis.sort(key=lambda x: x["total_value"], reverse=True)

            return {
                "num_communities": len(communities),
                "modularity": nx_comm.modularity(undirected, communities),
                "communities": community_analysis[:10],  # top 10 communities
                "largest_community_size": (
                    max(len(c) for c in communities) if communities else 0
                ),
            }

        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {}

    def _analyze_value_propagation(self) -> Dict[str, Any]:
        """Analyze how data value propagates through the graph"""
        if not self.graph:
            return {}

        try:
            # Calculate value propagation using weighted PageRank
            node_values = {
                n: self.graph.nodes[n].get("data_value", 0.0)
                for n in self.graph.nodes()
            }

            # Propagate values through the graph
            propagated_values = {}
            for node in self.graph.nodes():
                # Start with node's own value
                value = node_values[node]

                # Add weighted values from predecessors
                predecessors = list(self.graph.predecessors(node))
                if predecessors:
                    pred_values = [node_values[pred] for pred in predecessors]
                    value += 0.3 * np.mean(pred_values)  # 30% influence from parents

                # Add weighted values from successors (feedback)
                successors = list(self.graph.successors(node))
                if successors:
                    succ_values = [node_values[succ] for succ in successors]
                    value += 0.1 * np.mean(succ_values)  # 10% feedback from children

                propagated_values[node] = value

            # Find nodes with highest propagated values
            top_propagated = sorted(
                propagated_values.items(), key=lambda x: x[1], reverse=True
            )[:10]

            # Calculate value efficiency (propagated value / crawl cost)
            value_efficiency = {}
            for node, prop_value in propagated_values.items():
                response_time = self.graph.nodes[node].get("response_time", 1.0)
                efficiency = prop_value / max(
                    response_time, 0.1
                )  # avoid division by zero
                value_efficiency[node] = efficiency

            top_efficient = sorted(
                value_efficiency.items(), key=lambda x: x[1], reverse=True
            )[:10]

            return {
                "top_propagated_value": top_propagated,
                "top_value_efficient": top_efficient,
                "avg_propagated_value": np.mean(list(propagated_values.values())),
                "value_correlation": self._calculate_value_correlation(),
            }

        except Exception as e:
            logger.error(f"Value propagation analysis failed: {e}")
            return {}

    def _analyze_crawl_efficiency(self) -> Dict[str, Any]:
        """Analyze crawl efficiency and identify optimization opportunities"""
        if not self.graph:
            return {}

        try:
            # Calculate path efficiency
            successful_nodes = [
                n
                for n in self.graph.nodes()
                if self.graph.nodes[n].get("success", False)
            ]

            if len(successful_nodes) < 5:
                return {"status": "insufficient_successful_crawls"}

            # Analyze crawl depths
            depths = []
            for node in successful_nodes:
                try:
                    # Calculate shortest path from any root node
                    root_nodes = [
                        n for n in self.graph.nodes() if self.graph.in_degree(n) == 0
                    ]
                    if root_nodes:
                        min_depth = min(
                            nx.shortest_path_length(self.graph, root, node)
                            for root in root_nodes
                            if nx.has_path(self.graph, root, node)
                        )
                        depths.append(min_depth)
                except:
                    continue

            efficiency_metrics = {}
            if depths:
                efficiency_metrics.update(
                    {
                        "avg_crawl_depth": np.mean(depths),
                        "max_crawl_depth": np.max(depths),
                        "depth_distribution": Counter(depths),
                    }
                )

            # Analyze failed crawl patterns
            failed_nodes = [
                n
                for n in self.graph.nodes()
                if not self.graph.nodes[n].get("success", False)
            ]

            if failed_nodes:
                # Common failure patterns
                failed_domains = [self._extract_domain(url) for url in failed_nodes]
                domain_failures = Counter(failed_domains)

                efficiency_metrics.update(
                    {
                        "failure_rate": len(failed_nodes) / len(self.graph.nodes()),
                        "top_failing_domains": domain_failures.most_common(5),
                        "total_failed_crawls": len(failed_nodes),
                    }
                )

            return efficiency_metrics

        except Exception as e:
            logger.error(f"Efficiency analysis failed: {e}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on graph analysis"""
        recommendations = []

        if not self.graph:
            return ["Graph analysis not available - install NetworkX"]

        try:
            nodes = list(self.graph.nodes())
            if len(nodes) < self.min_nodes_for_analysis:
                return [
                    f"Collect more crawl data (current: {len(nodes)}, needed: {self.min_nodes_for_analysis})"
                ]

            # Success rate recommendations
            successful = sum(
                1 for n in nodes if self.graph.nodes[n].get("success", False)
            )
            success_rate = successful / len(nodes) if nodes else 0.0

            if success_rate < 0.7:
                recommendations.append(
                    f"Low success rate ({success_rate:.1%}) - review target selection and retry policies"
                )

            # Value efficiency recommendations
            node_values = [self.graph.nodes[n].get("data_value", 0.0) for n in nodes]
            avg_value = np.mean(node_values) if node_values else 0.0

            if avg_value < 0.3:
                recommendations.append(
                    "Low average data value - focus on higher-value targets"
                )

            # Graph density recommendations
            density = nx.density(self.graph)
            if density < 0.1:
                recommendations.append(
                    "Low graph connectivity - consider broader link discovery"
                )
            elif density > 0.5:
                recommendations.append(
                    "High graph density - implement more selective crawling"
                )

            # Community-based recommendations
            if len(nodes) > 50:
                try:
                    undirected = self.graph.to_undirected()
                    import networkx.algorithms.community as nx_comm

                    communities = list(
                        nx_comm.greedy_modularity_communities(undirected)
                    )

                    if len(communities) > 1:
                        # Find most valuable community
                        best_community = None
                        best_value = 0

                        for community in communities:
                            community_value = sum(
                                self.graph.nodes[n].get("data_value", 0.0)
                                for n in community
                            )
                            if community_value > best_value:
                                best_value = community_value
                                best_community = community

                        if best_community:
                            sample_domains = set(
                                self._extract_domain(url)
                                for url in list(best_community)[:5]
                            )
                            recommendations.append(
                                f"Focus on high-value community domains: {', '.join(sample_domains)}"
                            )

                except:
                    pass

            if not recommendations:
                recommendations.append(
                    "Crawl patterns look optimal - continue current strategy"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations - check logs"]

    def _get_centrality_distribution(
        self, pagerank: Dict[str, float]
    ) -> Dict[str, int]:
        """Get distribution of PageRank values"""
        values = list(pagerank.values())
        if not values:
            return {}

        # Create bins for distribution
        bins = np.linspace(min(values), max(values), 5)
        digitized = np.digitize(values, bins)

        distribution = {}
        for i in range(1, len(bins)):
            count = sum(1 for x in digitized if x == i)
            distribution[f"{bins[i-1]:.4f}-{bins[i]:.4f}"] = count

        return distribution

    def _calculate_value_correlation(self) -> float:
        """Calculate correlation between node connectivity and data value"""
        if not self.graph or len(self.graph.nodes()) < 10:
            return 0.0

        try:
            nodes = list(self.graph.nodes())
            connectivities = [self.graph.degree(n) for n in nodes]
            values = [self.graph.nodes[n].get("data_value", 0.0) for n in nodes]

            correlation = np.corrcoef(connectivities, values)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0

        except Exception as e:
            logger.error(f"Value correlation calculation failed: {e}")
            return 0.0

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse

            return urlparse(url).netloc
        except:
            return "unknown"

    def get_high_value_targets(self, limit: int = 20) -> List[Tuple[str, float]]:
        """Get URLs with highest predicted value based on graph analysis"""
        if not self.graph:
            return []

        try:
            # Use cached analysis or perform new one
            analysis = self.analyze_crawl_patterns()

            # Combine different metrics for target scoring
            target_scores = {}

            for node in self.graph.nodes():
                if (
                    self.graph.nodes[node].get("success") is not False
                ):  # not explicitly failed
                    score = 0.0

                    # Base value from node
                    score += self.graph.nodes[node].get("data_value", 0.0) * 0.4

                    # Connectivity bonus
                    degree = self.graph.degree(node)
                    score += min(degree / 10.0, 1.0) * 0.3  # normalize degree

                    # Success probability from neighbors
                    neighbors = list(self.graph.neighbors(node))
                    if neighbors:
                        neighbor_success = sum(
                            1
                            for n in neighbors
                            if self.graph.nodes[n].get("success", False)
                        )
                        score += (neighbor_success / len(neighbors)) * 0.3

                    target_scores[node] = score

            # Sort by score and return top targets
            top_targets = sorted(
                target_scores.items(), key=lambda x: x[1], reverse=True
            )
            return top_targets[:limit]

        except Exception as e:
            logger.error(f"High-value target identification failed: {e}")
            return []

    def export_graph(self, filepath: str, format: str = "gexf") -> bool:
        """Export graph to file for external analysis"""
        if not self.graph:
            return False

        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == "gexf":
                nx.write_gexf(self.graph, path)
            elif format.lower() == "gml":
                nx.write_gml(self.graph, path)
            elif format.lower() == "json":
                data = nx.node_link_data(self.graph)
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported graph to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Graph export failed: {e}")
            return False

    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get analyzer status and statistics"""
        stats = {
            "networkx_available": NETWORKX_AVAILABLE,
            "last_analysis": self.last_analysis,
            "cache_ttl": self.cache_ttl,
            "cached_analyses": len(self.analysis_cache),
        }

        if self.graph:
            stats.update(
                {
                    "graph_nodes": len(self.graph.nodes()),
                    "graph_edges": len(self.graph.edges()),
                    "graph_density": (
                        nx.density(self.graph) if len(self.graph.nodes()) > 1 else 0.0
                    ),
                }
            )
        else:
            stats.update({"graph_nodes": 0, "graph_edges": 0, "graph_density": 0.0})

        return stats
