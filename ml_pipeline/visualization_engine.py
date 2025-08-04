# Advanced Visualization Engine
# AI-powered charts, graphs, and interactive visualizations

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import base64
import io
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChartGenerator:
    """Generates various types of charts and visualizations"""
    
    def __init__(self):
        self.figure_size = (12, 8)
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def create_quality_distribution_chart(self, data: List[Dict[str, Any]]) -> str:
        """Create content quality distribution chart"""
        try:
            df = pd.DataFrame(data)
            if 'content_quality_score' not in df.columns:
                return ""
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Histogram
            ax1.hist(df['content_quality_score'], bins=20, alpha=0.7, color=self.color_palette[0])
            ax1.set_xlabel('Content Quality Score')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Content Quality Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Box plot by domain (if available)
            if 'domain' in df.columns:
                top_domains = df['domain'].value_counts().head(5).index
                filtered_df = df[df['domain'].isin(top_domains)]
                
                sns.boxplot(data=filtered_df, x='domain', y='content_quality_score', ax=ax2)
                ax2.set_title('Quality by Top Domains')
                ax2.set_xlabel('Domain')
                ax2.set_ylabel('Quality Score')
                plt.xticks(rotation=45)
            else:
                ax2.text(0.5, 0.5, 'Domain data not available', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Quality by Domain')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating quality distribution chart: {e}")
            return ""
    
    def create_clustering_visualization(self, clustering_data: Dict[str, Any]) -> str:
        """Create content clustering visualization"""
        try:
            if not clustering_data.get('clusters'):
                return ""
            
            clusters = clustering_data['clusters']
            
            # Prepare data for visualization
            cluster_names = []
            cluster_sizes = []
            cluster_quality = []
            
            for cluster_id, info in clusters.items():
                cluster_names.append(f"Cluster {cluster_id.split('_')[1]}")
                cluster_sizes.append(info['size'])
                cluster_quality.append(info['avg_quality_score'])
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Cluster sizes pie chart
            ax1.pie(cluster_sizes, labels=cluster_names, autopct='%1.1f%%', 
                   colors=self.color_palette[:len(cluster_sizes)])
            ax1.set_title('Content Cluster Distribution')
            
            # Quality by cluster bar chart
            bars = ax2.bar(cluster_names, cluster_quality, color=self.color_palette[:len(cluster_names)])
            ax2.set_xlabel('Clusters')
            ax2.set_ylabel('Average Quality Score')
            ax2.set_title('Quality Score by Cluster')
            ax2.set_ylim(0, 1)
            
            # Add value labels on bars
            for bar, quality in zip(bars, cluster_quality):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{quality:.3f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating clustering visualization: {e}")
            return ""
    
    def create_trend_analysis_chart(self, trend_data: Dict[str, Any]) -> str:
        """Create trend analysis visualization"""
        try:
            if not trend_data.get('hourly_patterns'):
                return ""
            
            hourly_data = trend_data['hourly_patterns']
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Quality trend by hour
            if 'content_quality_score' in hourly_data:
                hours = list(hourly_data['content_quality_score'].keys())
                quality_values = list(hourly_data['content_quality_score'].values())
                
                axes[0, 0].plot(hours, quality_values, marker='o', linewidth=2, color=self.color_palette[0])
                axes[0, 0].set_xlabel('Hour of Day')
                axes[0, 0].set_ylabel('Average Quality Score')
                axes[0, 0].set_title('Content Quality by Hour')
                axes[0, 0].grid(True, alpha=0.3)
            
            # Content length trend
            if 'content_length' in hourly_data:
                hours = list(hourly_data['content_length'].keys())
                length_values = list(hourly_data['content_length'].values())
                
                axes[0, 1].plot(hours, length_values, marker='s', linewidth=2, color=self.color_palette[1])
                axes[0, 1].set_xlabel('Hour of Day')
                axes[0, 1].set_ylabel('Average Content Length')
                axes[0, 1].set_title('Content Length by Hour')
                axes[0, 1].grid(True, alpha=0.3)
            
            # Image count trend
            if 'image_count' in hourly_data:
                hours = list(hourly_data['image_count'].keys())
                image_values = list(hourly_data['image_count'].values())
                
                axes[1, 0].bar(hours, image_values, alpha=0.7, color=self.color_palette[2])
                axes[1, 0].set_xlabel('Hour of Day')
                axes[1, 0].set_ylabel('Average Image Count')
                axes[1, 0].set_title('Images per Page by Hour')
            
            # Anomaly detection visualization
            if trend_data.get('anomalies'):
                anomaly_data = trend_data['anomalies']
                anomaly_count = anomaly_data.get('anomaly_count', 0)
                total_count = 100  # Placeholder
                normal_count = total_count - anomaly_count
                
                axes[1, 1].pie([normal_count, anomaly_count], 
                              labels=['Normal', 'Anomalous'], 
                              autopct='%1.1f%%',
                              colors=[self.color_palette[3], self.color_palette[4]])
                axes[1, 1].set_title('Anomaly Detection Results')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating trend analysis chart: {e}")
            return ""
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

class InteractiveChartGenerator:
    """Generates interactive charts using Plotly"""
    
    def __init__(self):
        self.template = "plotly_white"
        self.color_sequence = px.colors.qualitative.Set3
    
    def create_interactive_dashboard(self, insights_data: Dict[str, Any]) -> Dict[str, str]:
        """Create interactive dashboard charts"""
        charts = {}
        
        try:
            # Quality metrics chart
            charts['quality_metrics'] = self._create_quality_metrics_chart(insights_data)
            
            # Clustering analysis chart
            charts['clustering_3d'] = self._create_3d_clustering_chart(insights_data)
            
            # Real-time trends chart
            charts['realtime_trends'] = self._create_realtime_trends_chart(insights_data)
            
            # Performance heatmap
            charts['performance_heatmap'] = self._create_performance_heatmap(insights_data)
            
        except Exception as e:
            logger.error(f"Error creating interactive dashboard: {e}")
        
        return charts
    
    def _create_quality_metrics_chart(self, data: Dict[str, Any]) -> str:
        """Create interactive quality metrics chart"""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Quality Distribution', 'Quality vs Length', 
                               'Quality by Domain', 'Quality Trend'),
                specs=[[{"type": "histogram"}, {"type": "scatter"}],
                      [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # Sample data for demonstration
            quality_scores = np.random.beta(2, 5, 100)  # Simulated quality scores
            content_lengths = np.random.lognormal(6, 1, 100)  # Simulated content lengths
            
            # Quality distribution
            fig.add_trace(
                go.Histogram(x=quality_scores, name="Quality Distribution", 
                           marker_color=self.color_sequence[0]),
                row=1, col=1
            )
            
            # Quality vs Length scatter
            fig.add_trace(
                go.Scatter(x=content_lengths, y=quality_scores, mode='markers',
                          name="Quality vs Length", marker_color=self.color_sequence[1]),
                row=1, col=2
            )
            
            # Quality by domain (sample data)
            domains = ['domain1.com', 'domain2.com', 'domain3.com']
            domain_quality = [0.7, 0.5, 0.8]
            
            fig.add_trace(
                go.Bar(x=domains, y=domain_quality, name="Quality by Domain",
                       marker_color=self.color_sequence[2]),
                row=2, col=1
            )
            
            # Quality trend over time
            time_points = pd.date_range(start='2025-01-01', periods=30, freq='D')
            trend_values = 0.6 + 0.2 * np.sin(np.arange(30) * 0.2) + np.random.normal(0, 0.05, 30)
            
            fig.add_trace(
                go.Scatter(x=time_points, y=trend_values, mode='lines+markers',
                          name="Quality Trend", line_color=self.color_sequence[3]),
                row=2, col=2
            )
            
            fig.update_layout(
                title="Content Quality Analytics Dashboard",
                template=self.template,
                height=600,
                showlegend=False
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating quality metrics chart: {e}")
            return "{}"
    
    def _create_3d_clustering_chart(self, data: Dict[str, Any]) -> str:
        """Create 3D clustering visualization"""
        try:
            # Simulate 3D clustering data
            n_points = 100
            n_clusters = 5
            
            # Generate sample data
            cluster_data = []
            for i in range(n_clusters):
                cluster_points = np.random.multivariate_normal(
                    mean=[i*2, i*1.5, i*1.8], 
                    cov=[[0.5, 0, 0], [0, 0.5, 0], [0, 0, 0.5]], 
                    size=n_points//n_clusters
                )
                for point in cluster_points:
                    cluster_data.append({
                        'x': point[0], 'y': point[1], 'z': point[2], 
                        'cluster': f'Cluster {i+1}'
                    })
            
            df = pd.DataFrame(cluster_data)
            
            fig = px.scatter_3d(
                df, x='x', y='y', z='z', color='cluster',
                title="3D Content Clustering Analysis",
                color_discrete_sequence=self.color_sequence
            )
            
            fig.update_layout(
                template=self.template,
                height=600,
                scene=dict(
                    xaxis_title="Content Complexity",
                    yaxis_title="Quality Score", 
                    zaxis_title="Engagement Factor"
                )
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating 3D clustering chart: {e}")
            return "{}"
    
    def _create_realtime_trends_chart(self, data: Dict[str, Any]) -> str:
        """Create real-time trends chart"""
        try:
            # Generate sample real-time data
            timestamps = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                     end=datetime.now(), freq='10T')
            
            metrics = {
                'Quality Score': 0.6 + 0.2 * np.sin(np.arange(len(timestamps)) * 0.1) + np.random.normal(0, 0.05, len(timestamps)),
                'Processing Speed': 100 + 20 * np.cos(np.arange(len(timestamps)) * 0.15) + np.random.normal(0, 5, len(timestamps)),
                'Error Rate': 0.05 + 0.03 * np.abs(np.sin(np.arange(len(timestamps)) * 0.08)) + np.random.normal(0, 0.01, len(timestamps))
            }
            
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=list(metrics.keys()),
                vertical_spacing=0.1
            )
            
            colors = [self.color_sequence[0], self.color_sequence[1], self.color_sequence[2]]
            
            for i, (metric_name, values) in enumerate(metrics.items()):
                fig.add_trace(
                    go.Scatter(
                        x=timestamps, y=values,
                        mode='lines',
                        name=metric_name,
                        line=dict(color=colors[i], width=2)
                    ),
                    row=i+1, col=1
                )
            
            fig.update_layout(
                title="Real-time Performance Metrics",
                template=self.template,
                height=800,
                showlegend=False
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating real-time trends chart: {e}")
            return "{}"
    
    def _create_performance_heatmap(self, data: Dict[str, Any]) -> str:
        """Create performance heatmap"""
        try:
            # Generate sample performance data
            hours = list(range(24))
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Create performance matrix
            performance_matrix = np.random.rand(len(days), len(hours))
            
            fig = go.Figure(data=go.Heatmap(
                z=performance_matrix,
                x=[f"{h}:00" for h in hours],
                y=days,
                colorscale='Viridis',
                hoverongaps=False,
                hovertemplate='Day: %{y}<br>Hour: %{x}<br>Performance: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Performance Heatmap (24h x 7 days)",
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week",
                template=self.template,
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating performance heatmap: {e}")
            return "{}"

class AIInsightVisualizer:
    """AI-powered insights visualization"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.interactive_generator = InteractiveChartGenerator()
    
    def create_comprehensive_visualization_suite(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive visualization suite"""
        try:
            visualization_suite = {
                'static_charts': {
                    'quality_distribution': '',
                    'clustering_analysis': '',
                    'trend_analysis': ''
                },
                'interactive_charts': {},
                'summary_stats': self._generate_summary_stats(insights_data),
                'recommendations_chart': self._create_recommendations_visualization(insights_data)
            }
            
            # Generate static charts
            if insights_data.get('data_statistics'):
                sample_data = self._create_sample_data(insights_data['data_statistics'])
                visualization_suite['static_charts']['quality_distribution'] = \
                    self.chart_generator.create_quality_distribution_chart(sample_data)
            
            if insights_data.get('clustering'):
                visualization_suite['static_charts']['clustering_analysis'] = \
                    self.chart_generator.create_clustering_visualization(insights_data['clustering'])
            
            if insights_data.get('trends'):
                visualization_suite['static_charts']['trend_analysis'] = \
                    self.chart_generator.create_trend_analysis_chart(insights_data['trends'])
            
            # Generate interactive charts
            visualization_suite['interactive_charts'] = \
                self.interactive_generator.create_interactive_dashboard(insights_data)
            
            return visualization_suite
            
        except Exception as e:
            logger.error(f"Error creating visualization suite: {e}")
            return {}
    
    def _generate_summary_stats(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for visualization"""
        stats = {}
        
        if insights_data.get('data_statistics'):
            data_stats = insights_data['data_statistics']
            stats.update({
                'total_items': data_stats.get('total_items', 0),
                'avg_quality': data_stats.get('avg_quality_score', 0),
                'domains_count': data_stats.get('domains_analyzed', 0)
            })
        
        if insights_data.get('clustering'):
            clustering = insights_data['clustering']
            stats.update({
                'silhouette_score': clustering.get('silhouette_score', 0),
                'cluster_count': len(clustering.get('clusters', {}))
            })
        
        return stats
    
    def _create_sample_data(self, data_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create sample data for visualization"""
        total_items = data_stats.get('total_items', 100)
        avg_quality = data_stats.get('avg_quality_score', 0.5)
        
        # Generate sample data based on statistics
        sample_data = []
        for i in range(min(total_items, 100)):  # Limit to 100 samples
            sample_data.append({
                'content_quality_score': max(0, min(1, np.random.normal(avg_quality, 0.2))),
                'content_length': np.random.lognormal(6, 1),
                'image_count': np.random.poisson(2),
                'link_count': np.random.poisson(5),
                'domain': f"domain{np.random.randint(1, 6)}.com",
                'has_images': np.random.random() > 0.3,
                'has_links': np.random.random() > 0.2
            })
        
        return sample_data
    
    def _create_recommendations_visualization(self, insights_data: Dict[str, Any]) -> str:
        """Create visualization for recommendations"""
        try:
            recommendations = insights_data.get('recommendations', [])
            
            if not recommendations:
                return ""
            
            # Create a simple bar chart showing recommendation priorities
            rec_categories = ['Quality', 'Content', 'Media', 'Links', 'Structure']
            rec_scores = [0.8, 0.6, 0.7, 0.5, 0.9]  # Sample priority scores
            
            fig = go.Figure(data=[
                go.Bar(
                    x=rec_categories,
                    y=rec_scores,
                    marker_color=self.interactive_generator.color_sequence[:len(rec_categories)]
                )
            ])
            
            fig.update_layout(
                title="Improvement Recommendations Priority",
                xaxis_title="Improvement Areas",
                yaxis_title="Priority Score",
                template=self.interactive_generator.template,
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            logger.error(f"Error creating recommendations visualization: {e}")
            return ""

# Export main classes
__all__ = [
    'ChartGenerator',
    'InteractiveChartGenerator', 
    'AIInsightVisualizer'
]
