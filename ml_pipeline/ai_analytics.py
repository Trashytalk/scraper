# Machine Learning Pipeline
# Advanced Analytics & AI Integration - Phase 4

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import silhouette_score
import joblib
import json
import logging
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MLDataProcessor:
    """Advanced data processing for machine learning"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        
    def process_scraped_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process scraped data for ML analysis"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Extract features
            processed_data = []
            
            for item in data:
                features = {
                    'content_length': len(str(item.get('content', ''))),
                    'title_length': len(str(item.get('title', ''))),
                    'has_images': bool(item.get('images')),
                    'image_count': len(item.get('images', [])),
                    'has_links': bool(item.get('links')),
                    'link_count': len(item.get('links', [])),
                    'timestamp': datetime.now().isoformat(),
                    'domain': self._extract_domain(item.get('url', '')),
                    'content_quality_score': self._calculate_content_quality(item),
                    'text_content': str(item.get('content', ''))[:1000],  # Limit for TF-IDF
                }
                processed_data.append(features)
            
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            logger.error(f"Error processing scraped data: {e}")
            return pd.DataFrame()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _calculate_content_quality(self, item: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        score = 0.0
        
        # Content length score
        content = str(item.get('content', ''))
        if len(content) > 1000:
            score += 0.3
        elif len(content) > 500:
            score += 0.2
        elif len(content) > 100:
            score += 0.1
        
        # Title quality
        title = str(item.get('title', ''))
        if len(title) > 10:
            score += 0.2
        
        # Media content
        if item.get('images'):
            score += 0.2
        
        # Link richness
        if item.get('links'):
            score += 0.1
        
        # Structure indicators
        if any(tag in content.lower() for tag in ['<h1>', '<h2>', '<p>', '<div>']):
            score += 0.2
        
        return min(score, 1.0)

class ContentClusteringEngine:
    """AI-powered content clustering and analysis"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.pca = PCA(n_components=2)
        
    def analyze_content_clusters(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform content clustering analysis"""
        try:
            if df.empty or 'text_content' not in df.columns:
                return {}
            
            # Vectorize text content
            text_data = df['text_content'].fillna('').tolist()
            X_text = self.vectorizer.fit_transform(text_data)
            
            # Perform clustering
            clusters = self.kmeans.fit_predict(X_text)
            df['cluster'] = clusters
            
            # Calculate silhouette score
            silhouette_avg = silhouette_score(X_text, clusters)
            
            # Get cluster centers and top terms
            feature_names = self.vectorizer.get_feature_names_out()
            cluster_info = {}
            
            for i in range(self.n_clusters):
                cluster_mask = clusters == i
                cluster_size = np.sum(cluster_mask)
                
                # Get top terms for this cluster
                center = self.kmeans.cluster_centers_[i]
                top_indices = center.argsort()[-10:][::-1]
                top_terms = [feature_names[idx] for idx in top_indices]
                
                cluster_info[f"cluster_{i}"] = {
                    "size": int(cluster_size),
                    "percentage": float(cluster_size / len(df) * 100),
                    "top_terms": top_terms,
                    "avg_quality_score": float(df[cluster_mask]['content_quality_score'].mean()) if cluster_size > 0 else 0.0
                }
            
            # Generate insights
            insights = self._generate_clustering_insights(cluster_info, df)
            
            return {
                "clusters": cluster_info,
                "silhouette_score": float(silhouette_avg),
                "total_documents": len(df),
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in content clustering: {e}")
            return {}
    
    def _generate_clustering_insights(self, cluster_info: Dict, df: pd.DataFrame) -> List[str]:
        """Generate intelligent insights from clustering results"""
        insights = []
        
        # Find largest cluster
        largest_cluster = max(cluster_info.values(), key=lambda x: x['size'])
        insights.append(f"📊 Largest content cluster represents {largest_cluster['percentage']:.1f}% of data")
        
        # Find highest quality cluster
        highest_quality = max(cluster_info.values(), key=lambda x: x['avg_quality_score'])
        insights.append(f"⭐ Highest quality content cluster has {highest_quality['avg_quality_score']:.2f} average score")
        
        # Domain diversity analysis
        domains = df['domain'].value_counts()
        if len(domains) > 1:
            insights.append(f"🌐 Content spans {len(domains)} different domains")
        
        # Content length analysis
        avg_length = df['content_length'].mean()
        insights.append(f"📝 Average content length: {avg_length:.0f} characters")
        
        return insights

class PredictiveAnalytics:
    """Predictive analytics and forecasting"""
    
    def __init__(self):
        self.trend_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
    def analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data trends and patterns"""
        try:
            if df.empty:
                return {}
            
            # Time-based analysis
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Trend analysis
            hourly_stats = df.groupby('hour').agg({
                'content_quality_score': 'mean',
                'content_length': 'mean',
                'image_count': 'mean'
            }).to_dict()
            
            # Quality trend prediction
            quality_trend = self._predict_quality_trend(df)
            
            # Anomaly detection
            anomalies = self._detect_anomalies(df)
            
            return {
                "hourly_patterns": hourly_stats,
                "quality_trend": quality_trend,
                "anomalies": anomalies,
                "total_analyzed": len(df),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {}
    
    def _predict_quality_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict content quality trends"""
        try:
            if len(df) < 5:
                return {"prediction": "insufficient_data"}
            
            # Prepare features for prediction
            features = ['content_length', 'image_count', 'link_count', 'hour']
            X = df[features].fillna(0)
            y = df['content_quality_score']
            
            # Train model
            self.trend_model.fit(X, y)
            
            # Feature importance
            importance = dict(zip(features, self.trend_model.feature_importances_))
            
            # Predict future quality
            future_prediction = self.trend_model.predict(X.tail(1))[0]
            
            return {
                "predicted_quality": float(future_prediction),
                "feature_importance": {k: float(v) for k, v in importance.items()},
                "model_score": float(self.trend_model.score(X, y))
            }
            
        except Exception as e:
            logger.error(f"Error in quality prediction: {e}")
            return {"prediction": "error"}
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalous content"""
        try:
            features = ['content_length', 'content_quality_score', 'image_count', 'link_count']
            X = df[features].fillna(0)
            
            # Detect anomalies
            anomaly_labels = self.anomaly_detector.fit_predict(X)
            anomaly_count = np.sum(anomaly_labels == -1)
            
            return {
                "anomaly_count": int(anomaly_count),
                "anomaly_percentage": float(anomaly_count / len(df) * 100),
                "anomaly_indices": [int(i) for i, label in enumerate(anomaly_labels) if label == -1]
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {}

class AIInsightsGenerator:
    """AI-powered insights and recommendations"""
    
    def __init__(self):
        self.processor = MLDataProcessor()
        self.clustering = ContentClusteringEngine()
        self.analytics = PredictiveAnalytics()
    
    async def generate_comprehensive_insights(self, scraped_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive AI insights from scraped data"""
        try:
            # Process data
            df = self.processor.process_scraped_data(scraped_data)
            
            if df.empty:
                return {"error": "No data to analyze"}
            
            # Run all analyses
            clustering_results = self.clustering.analyze_content_clusters(df)
            trend_analysis = self.analytics.analyze_trends(df)
            
            # Generate summary insights
            summary_insights = self._generate_summary_insights(df, clustering_results, trend_analysis)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(df, clustering_results, trend_analysis)
            
            return {
                "summary": summary_insights,
                "clustering": clustering_results,
                "trends": trend_analysis,
                "recommendations": recommendations,
                "data_statistics": {
                    "total_items": len(df),
                    "avg_quality_score": float(df['content_quality_score'].mean()),
                    "domains_analyzed": len(df['domain'].unique()),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {"error": str(e)}
    
    def _generate_summary_insights(self, df: pd.DataFrame, clustering: Dict, trends: Dict) -> List[str]:
        """Generate high-level summary insights"""
        insights = []
        
        # Data overview
        insights.append(f"🔍 Analyzed {len(df)} web pages from {len(df['domain'].unique())} domains")
        
        # Quality assessment
        avg_quality = df['content_quality_score'].mean()
        if avg_quality > 0.7:
            insights.append("⭐ High-quality content detected across most pages")
        elif avg_quality > 0.4:
            insights.append("📊 Mixed quality content with optimization opportunities")
        else:
            insights.append("⚠️ Content quality below average, consider source improvements")
        
        # Content patterns
        if clustering.get('clusters'):
            best_cluster = max(clustering['clusters'].values(), key=lambda x: x['avg_quality_score'])
            insights.append(f"🎯 Best content cluster focuses on: {', '.join(best_cluster['top_terms'][:3])}")
        
        # Trend insights
        if trends.get('anomalies', {}).get('anomaly_count', 0) > 0:
            anomaly_pct = trends['anomalies']['anomaly_percentage']
            insights.append(f"🚨 {anomaly_pct:.1f}% of content shows unusual patterns")
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame, clustering: Dict, trends: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Quality improvements
        low_quality_count = len(df[df['content_quality_score'] < 0.3])
        if low_quality_count > 0:
            recommendations.append(f"📈 Improve {low_quality_count} low-quality pages by adding more content and media")
        
        # Content gaps
        if clustering.get('clusters'):
            small_clusters = [c for c in clustering['clusters'].values() if c['size'] < len(df) * 0.1]
            if small_clusters:
                recommendations.append(f"🎯 Focus on underrepresented content areas for better coverage")
        
        # Media optimization
        no_images = len(df[df['image_count'] == 0])
        if no_images > len(df) * 0.5:
            recommendations.append("🖼️ Add more visual content - 50%+ of pages lack images")
        
        # Link building
        no_links = len(df[df['link_count'] == 0])
        if no_links > len(df) * 0.3:
            recommendations.append("🔗 Improve internal linking - 30%+ of pages have no links")
        
        return recommendations

# Export main classes
__all__ = [
    'MLDataProcessor',
    'ContentClusteringEngine', 
    'PredictiveAnalytics',
    'AIInsightsGenerator'
]
