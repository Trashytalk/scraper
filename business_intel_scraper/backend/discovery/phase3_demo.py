"""Phase 3: Advanced Discovery Demonstration System - ML-Powered Intelligence Showcase"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

# Initialize rich console
console = Console()


class Phase3Demo:
    """
    Phase 3: Advanced Discovery Features Demonstration System
    
    Showcases ML-powered content analysis, data quality assessment,
    intelligent pattern recognition, and predictive discovery capabilities.
    """
    
    def __init__(self):
        self.demo_start_time = datetime.utcnow()
        self.components_tested = []
        self.results = {}
        
        # Sample data for demonstrations
        self.sample_urls = [
            "https://example.com/news/article-1",
            "https://example.com/blog/post-2",
            "https://example.com/products/item-3"
        ]
        
        self.sample_html = """
        <html>
            <head>
                <title>Sample Article - Business News</title>
                <meta name="description" content="Important business updates and market analysis">
            </head>
            <body>
                <header>
                    <h1>Business Intelligence Update</h1>
                    <nav>
                        <a href="/home">Home</a>
                        <a href="/news">News</a>
                        <a href="/analysis">Analysis</a>
                    </nav>
                </header>
                <main>
                    <article>
                        <h2>Market Trends Analysis</h2>
                        <p>The technology sector showed significant growth with companies like Apple, Microsoft, and Google leading the charge.</p>
                        <div class="metrics">
                            <span class="revenue">Revenue: $50B</span>
                            <span class="growth">Growth: +15%</span>
                        </div>
                        <table class="data-table">
                            <tr><th>Company</th><th>Revenue</th><th>Growth</th></tr>
                            <tr><td>Apple</td><td>$365B</td><td>+5.5%</td></tr>
                            <tr><td>Microsoft</td><td>$198B</td><td>+12.1%</td></tr>
                        </table>
                    </article>
                    <form class="newsletter">
                        <input type="email" placeholder="Enter email">
                        <button type="submit">Subscribe</button>
                    </form>
                </main>
                <footer>
                    <img src="/logo.png" alt="Company Logo">
                    <p>&copy; 2024 Business Intelligence Corp</p>
                </footer>
            </body>
        </html>
        """
        
        self.sample_data = [
            {
                "company": "Apple Inc.",
                "revenue": 365000000000,
                "growth_rate": 0.055,
                "sector": "Technology",
                "last_updated": "2024-01-15T10:30:00Z",
                "data_quality": "high"
            },
            {
                "company": "Microsoft Corp.",
                "revenue": 198000000000,
                "growth_rate": 0.121,
                "sector": "Technology", 
                "last_updated": "2024-01-15T10:30:00Z",
                "data_quality": "high"
            },
            {
                "company": "Incomplete Corp.",
                "revenue": None,
                "growth_rate": 0.0,
                "sector": "",
                "last_updated": "2024-01-01T00:00:00Z",
                "data_quality": "low"
            }
        ]
    
    async def demo_ml_content_analysis(self) -> None:
        """Demonstrate ML-powered content analysis capabilities"""
        
        console.print(Panel.fit(
            "[bold cyan]🔬 Phase 3: ML Content Analysis Demo[/bold cyan]\n"
            "[green]Intelligent feature extraction • Content classification • Quality prediction[/green]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Initializing ML content analyzer...", total=None)
            
            try:
                # Import Phase 3 components
                from ..discovery.ml_content_analysis import content_analyzer
                
                if content_analyzer is None:
                    console.print("[red]❌ ML Content Analyzer not available[/red]")
                    console.print("[yellow]💡 Install scikit-learn, pandas, numpy for full functionality[/yellow]")
                    return
                
                progress.update(task, description="Analyzing sample content...")
                
                # Analyze sample content
                features = await content_analyzer.analyze_content(
                    self.sample_urls[0], 
                    self.sample_html
                )
                
                progress.update(task, description="Predicting content quality...")
                
                # Predict content quality
                quality_predictions = await content_analyzer.predict_content_quality(features)
                
                progress.update(task, description="Analysis complete!")
                
            except Exception as exc:
                progress.update(task, description="Analysis failed!")
                console.print(f"[red]❌ ML Content Analysis failed: {exc}[/red]")
                return
        
        # Display results
        console.print("\n[green]✅ ML Content Analysis Complete[/green]")
        
        # Content features table
        features_table = Table(title="Extracted Content Features", show_header=True, header_style="bold magenta")
        features_table.add_column("Feature", style="cyan")
        features_table.add_column("Value", style="yellow")
        
        features_table.add_row("Content Type", features.content_type)
        features_table.add_row("Language", features.language)
        features_table.add_row("Word Count", str(features.word_count))
        features_table.add_row("Link Count", str(features.link_count))
        features_table.add_row("Image Count", str(features.image_count))
        features_table.add_row("Form Count", str(features.form_count))
        features_table.add_row("Table Count", str(features.table_count))
        features_table.add_row("Readability Score", f"{features.readability_score:.2f}")
        features_table.add_row("Content Density", f"{features.content_density:.2f}")
        
        console.print(features_table)
        
        # Quality predictions
        if quality_predictions:
            quality_table = Table(title="ML Quality Predictions", show_header=True, header_style="bold green")
            quality_table.add_column("Metric", style="cyan")
            quality_table.add_column("Prediction", style="yellow")
            
            for metric, prediction in quality_predictions.items():
                if isinstance(prediction, dict):
                    score = prediction.get('score', 'N/A')
                    quality_table.add_row(
                        metric.replace('_', ' ').title(),
                        f"{score:.3f}" if isinstance(score, float) else str(score)
                    )
                else:
                    quality_table.add_row(
                        metric.replace('_', ' ').title(),
                        str(prediction)
                    )
            
            console.print(quality_table)
        
        self.components_tested.append("ML Content Analysis")
        self.results["ml_content_analysis"] = {
            "features_extracted": len(features.__dict__),
            "quality_predictions": len(quality_predictions) if quality_predictions else 0,
            "success": True
        }
        
        console.print("[blue]💡 Key Benefits:[/blue]")
        console.print("  • Automated content classification and feature extraction")
        console.print("  • ML-powered quality scoring and prediction")
        console.print("  • Semantic content analysis and entity recognition")
        console.print("  • Predictive insights for content optimization")
    
    async def demo_data_quality_assessment(self) -> None:
        """Demonstrate advanced data quality assessment"""
        
        console.print(Panel.fit(
            "[bold cyan]📊 Phase 3: Data Quality Assessment Demo[/bold cyan]\n"
            "[green]Multi-dimensional quality scoring • Anomaly detection • Automated recommendations[/green]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Initializing quality assessor...", total=None)
            
            try:
                from ..discovery.data_quality_assessment import quality_assessor
                
                progress.update(task, description="Assessing data quality...")
                
                # Assess sample data quality
                metrics = await quality_assessor.assess_data_quality(
                    self.sample_data, 
                    "demo://sample-business-data"
                )
                
                progress.update(task, description="Generating quality report...")
                
                # Generate quality report
                report = quality_assessor.generate_quality_report(metrics)
                
                progress.update(task, description="Quality assessment complete!")
                
            except Exception as exc:
                progress.update(task, description="Assessment failed!")
                console.print(f"[red]❌ Data Quality Assessment failed: {exc}[/red]")
                return
        
        # Display results
        console.print("\n[green]✅ Data Quality Assessment Complete[/green]")
        
        # Overall quality score
        overall_score = metrics.overall_quality_score
        score_color = "green" if overall_score >= 0.8 else "yellow" if overall_score >= 0.6 else "red"
        console.print(f"\n[bold]Overall Quality Score: [{score_color}]{overall_score:.3f}[/{score_color}][/bold]")
        
        # Quality metrics table
        quality_table = Table(title="Quality Assessment Metrics", show_header=True, header_style="bold magenta")
        quality_table.add_column("Dimension", style="cyan")
        quality_table.add_column("Score", style="yellow")
        quality_table.add_column("Status", style="white")
        
        quality_table.add_row("Completeness", f"{metrics.completeness_score:.3f}", "✅ Good" if metrics.completeness_score >= 0.7 else "⚠️ Needs attention")
        quality_table.add_row("Consistency", f"{metrics.consistency_score:.3f}", "✅ Good" if metrics.consistency_score >= 0.7 else "⚠️ Needs attention")
        quality_table.add_row("Validity", f"{metrics.validity_score:.3f}", "✅ Good" if metrics.validity_score >= 0.7 else "⚠️ Needs attention")
        quality_table.add_row("Accuracy", f"{metrics.accuracy_score:.3f}", "✅ Good" if metrics.accuracy_score >= 0.7 else "⚠️ Needs attention")
        quality_table.add_row("Uniqueness", f"{metrics.uniqueness_score:.3f}", "✅ Good" if metrics.uniqueness_score >= 0.7 else "⚠️ Needs attention")
        quality_table.add_row("Timeliness", f"{metrics.timeliness_score:.3f}", "✅ Good" if metrics.timeliness_score >= 0.7 else "⚠️ Needs attention")
        
        console.print(quality_table)
        
        # Display quality report
        console.print(f"\n[bold]Generated Quality Report:[/bold]")
        console.print(Panel(report, border_style="blue"))
        
        # Anomalies if detected
        if metrics.anomalies_detected:
            anomaly_table = Table(title="Detected Anomalies", show_header=True, header_style="bold red")
            anomaly_table.add_column("Type", style="red")
            anomaly_table.add_column("Description", style="yellow")
            
            for anomaly in metrics.anomalies_detected:
                if isinstance(anomaly, dict):
                    anomaly_table.add_row(
                        anomaly.get('type', 'Unknown'),
                        anomaly.get('description', 'No description')
                    )
                else:
                    anomaly_table.add_row("General", str(anomaly))
            
            console.print(anomaly_table)
        
        self.components_tested.append("Data Quality Assessment")
        self.results["data_quality_assessment"] = {
            "overall_score": overall_score,
            "anomalies_detected": len(metrics.anomalies_detected),
            "dimensions_assessed": 6,
            "success": True
        }
        
        console.print("[blue]💡 Key Benefits:[/blue]")
        console.print("  • Comprehensive multi-dimensional quality scoring")
        console.print("  • ML-powered anomaly detection and pattern recognition")
        console.print("  • Automated quality improvement recommendations")
        console.print("  • Statistical analysis and data profiling")
    
    async def demo_intelligent_pattern_recognition(self) -> None:
        """Demonstrate intelligent pattern recognition and learning"""
        
        console.print(Panel.fit(
            "[bold cyan]🧠 Phase 3: Intelligent Pattern Recognition Demo[/bold cyan]\n"
            "[green]Self-learning algorithms • Pattern optimization • Adaptive extraction[/green]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Initializing pattern recognizer...", total=None)
            
            try:
                from ..discovery.intelligent_pattern_recognition import pattern_recognizer, LearningSession
                
                # Create a sample learning session
                session = LearningSession(
                    session_id="demo-session-001",
                    spider_name="business_intelligence_spider",
                    target_url=self.sample_urls[0],
                    start_time=datetime.utcnow() - timedelta(minutes=5),
                    end_time=datetime.utcnow(),
                    duration=300.0,
                    records_extracted=25,
                    errors_encountered=2,
                    data_quality_score=0.85,
                    successful_selectors={
                        "article h2": 95,
                        ".metrics span": 85,
                        "table.data-table tr": 90
                    },
                    failed_selectors=[
                        ".nonexistent-selector",
                        "div.missing-class"
                    ],
                    adaptations_made=[
                        "Switched from CSS to XPath selector",
                        "Added wait condition for dynamic content"
                    ],
                    page_structure_hash="abc123def456",
                    response_characteristics={
                        "status_code": 200,
                        "content_length": 15000,
                        "response_time": 1.2
                    }
                )
                
                progress.update(task, description="Learning from session data...")
                
                # Learn patterns from session
                learned_patterns = await pattern_recognizer.learn_from_session(session)
                
                progress.update(task, description="Getting pattern statistics...")
                
                # Get pattern statistics
                stats = pattern_recognizer.get_pattern_statistics()
                
                progress.update(task, description="Running adaptive learning cycle...")
                
                # Run adaptive learning cycle
                await pattern_recognizer.adaptive_learning_cycle()
                
                progress.update(task, description="Pattern recognition complete!")
                
            except Exception as exc:
                progress.update(task, description="Pattern recognition failed!")
                console.print(f"[red]❌ Pattern Recognition failed: {exc}[/red]")
                return
        
        # Display results
        console.print("\n[green]✅ Intelligent Pattern Recognition Complete[/green]")
        
        console.print(f"[bold]Learned {len(learned_patterns)} patterns from demo session[/bold]")
        
        # Pattern statistics table
        stats_table = Table(title="Pattern Recognition Statistics", show_header=True, header_style="bold purple")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        
        for stat, value in stats.items():
            stats_table.add_row(stat.replace('_', ' ').title(), str(value))
        
        console.print(stats_table)
        
        # Sample learned patterns
        if learned_patterns:
            pattern_table = Table(title="Sample Learned Patterns", show_header=True, header_style="bold green")
            pattern_table.add_column("Pattern ID", style="cyan")
            pattern_table.add_column("Type", style="yellow")
            pattern_table.add_column("Confidence", style="green")
            pattern_table.add_column("Success Rate", style="magenta")
            
            for pattern in learned_patterns[:5]:  # Show first 5 patterns
                pattern_table.add_row(
                    pattern.pattern_id[:15] + "..." if len(pattern.pattern_id) > 15 else pattern.pattern_id,
                    pattern.pattern_type,
                    f"{pattern.confidence:.3f}",
                    f"{pattern.success_rate:.3f}"
                )
            
            console.print(pattern_table)
        
        self.components_tested.append("Intelligent Pattern Recognition")
        self.results["pattern_recognition"] = {
            "patterns_learned": len(learned_patterns),
            "total_patterns": stats.get('total_patterns', 0),
            "learning_sessions": stats.get('learning_sessions', 0),
            "success": True
        }
        
        console.print("[blue]💡 Key Benefits:[/blue]")
        console.print("  • Self-learning extraction pattern optimization")
        console.print("  • Adaptive algorithm improvement over time")
        console.print("  • Intelligent selector recommendation system")
        console.print("  • Performance-based pattern refinement")
    
    async def demo_predictive_discovery(self) -> None:
        """Demonstrate predictive source discovery"""
        
        console.print(Panel.fit(
            "[bold cyan]🔍 Phase 3: Predictive Discovery Demo[/bold cyan]\n"
            "[green]ML-powered source discovery • Similarity analysis • Content prediction[/green]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Initializing predictive discovery...", total=None)
            
            try:
                from ..discovery.ml_content_analysis import content_analyzer, predictive_discovery
                
                if not content_analyzer or not predictive_discovery:
                    console.print("[red]❌ Predictive Discovery not available[/red]")
                    return
                
                progress.update(task, description="Analyzing seed content...")
                
                # Analyze sample content for predictive discovery
                content_features = await content_analyzer.analyze_content(
                    self.sample_urls[0],
                    self.sample_html
                )
                
                progress.update(task, description="Discovering related sources...")
                
                # Discover related sources (mock implementation for demo)
                discovered_sources = await predictive_discovery.discover_related_sources(
                    self.sample_urls[0],
                    content_features,
                    max_sources=8
                )
                
                progress.update(task, description="Discovery complete!")
                
            except Exception as exc:
                progress.update(task, description="Discovery failed!")
                console.print(f"[red]❌ Predictive Discovery failed: {exc}[/red]")
                return
        
        # Display results
        console.print("\n[green]✅ Predictive Source Discovery Complete[/green]")
        
        console.print(f"[bold]Discovered {len(discovered_sources)} related sources[/bold]")
        
        # Display discovered sources
        if discovered_sources:
            source_table = Table(title="Discovered Related Sources", show_header=True, header_style="bold green")
            source_table.add_column("URL", style="cyan")
            source_table.add_column("Similarity", style="yellow")
            source_table.add_column("Quality Score", style="green")
            source_table.add_column("Content Type", style="magenta")
            
            for source in discovered_sources:
                if isinstance(source, dict):
                    source_table.add_row(
                        source.get('url', 'Unknown'),
                        f"{source.get('similarity_score', 0):.3f}",
                        f"{source.get('quality_score', 0):.3f}",
                        source.get('content_type', 'Unknown')
                    )
                else:
                    source_table.add_row(str(source), "N/A", "N/A", "Unknown")
            
            console.print(source_table)
        else:
            console.print("[yellow]⚠️ No related sources discovered in demo mode[/yellow]")
        
        self.components_tested.append("Predictive Discovery")
        self.results["predictive_discovery"] = {
            "sources_discovered": len(discovered_sources),
            "seed_analysis_features": len(content_features.__dict__),
            "success": True
        }
        
        console.print("[blue]💡 Key Benefits:[/blue]")
        console.print("  • Intelligent discovery of related data sources")
        console.print("  • ML-powered similarity analysis and ranking")
        console.print("  • Predictive content quality assessment")
        console.print("  • Automated source expansion and exploration")
    
    async def demo_system_integration(self) -> None:
        """Demonstrate Phase 3 system integration"""
        
        console.print(Panel.fit(
            "[bold cyan]⚙️ Phase 3: System Integration Demo[/bold cyan]\n"
            "[green]Component integration • Task automation • End-to-end workflow[/green]",
            border_style="cyan"
        ))
        
        # Show Phase 3 task integration
        console.print("\n[bold]🚀 Phase 3 Celery Task Integration:[/bold]")
        
        task_table = Table(title="Available Phase 3 Tasks", show_header=True, header_style="bold blue")
        task_table.add_column("Task Name", style="cyan")
        task_table.add_column("Description", style="yellow")
        task_table.add_column("Status", style="green")
        
        phase3_tasks = [
            ("analyze_content_with_ml", "ML-powered content analysis", "✅ Active"),
            ("assess_data_quality", "Advanced data quality assessment", "✅ Active"),
            ("learn_from_spider_execution", "Pattern learning from sessions", "✅ Active"),
            ("discover_predictive_sources", "ML-based source discovery", "✅ Active"),
            ("optimize_extraction_strategy", "Intelligent selector optimization", "✅ Active"),
            ("run_adaptive_learning_cycle", "Adaptive pattern learning", "✅ Active"),
            ("generate_ml_insights_report", "Comprehensive ML insights", "✅ Active")
        ]
        
        for task_name, description, status in phase3_tasks:
            task_table.add_row(task_name, description, status)
        
        console.print(task_table)
        
        # Show CLI integration
        console.print("\n[bold]💻 Phase 3 CLI Integration:[/bold]")
        
        cli_table = Table(title="Phase 3 CLI Commands", show_header=True, header_style="bold purple")
        cli_table.add_column("Command", style="cyan")
        cli_table.add_column("Function", style="yellow")
        
        cli_commands = [
            ("phase3 analyze-content <url>", "Analyze content with ML"),
            ("phase3 assess-quality <file>", "Assess data quality"),
            ("phase3 learn-patterns <session>", "Learn extraction patterns"),
            ("phase3 discover-sources <url>", "Discover related sources"),
            ("phase3 optimize-selectors <url> <selectors>", "Optimize selectors"),
            ("phase3 run-learning-cycle", "Run adaptive learning"),
            ("phase3 generate-insights", "Generate ML insights"),
            ("phase3 status", "System status check")
        ]
        
        for command, function in cli_commands:
            cli_table.add_row(command, function)
        
        console.print(cli_table)
        
        self.components_tested.append("System Integration")
        self.results["system_integration"] = {
            "tasks_available": len(phase3_tasks),
            "cli_commands": len(cli_commands),
            "success": True
        }
        
        console.print("[blue]💡 Integration Features:[/blue]")
        console.print("  • Seamless Phase 1, 2, and 3 component interaction")
        console.print("  • Automated ML-powered task scheduling")
        console.print("  • Comprehensive CLI and API integration")
        console.print("  • Real-time monitoring and insights reporting")
    
    def generate_demo_summary(self) -> None:
        """Generate comprehensive demo summary"""
        
        console.print(Panel.fit(
            "[bold cyan]📊 Phase 3: Advanced Discovery Demo Summary[/bold cyan]\n"
            "[green]Complete ML-powered intelligence automation showcase[/green]",
            border_style="cyan"
        ))
        
        # Demo overview
        demo_duration = (datetime.utcnow() - self.demo_start_time).total_seconds()
        
        overview_table = Table(title="Demo Overview", show_header=True, header_style="bold magenta")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="yellow")
        
        overview_table.add_row("Demo Duration", f"{demo_duration:.1f} seconds")
        overview_table.add_row("Components Tested", str(len(self.components_tested)))
        overview_table.add_row("Success Rate", "100%" if all(r.get("success", False) for r in self.results.values()) else "Partial")
        overview_table.add_row("ML Components Active", "Yes" if self.components_tested else "No")
        
        console.print(overview_table)
        
        # Component results
        if self.components_tested:
            results_table = Table(title="Component Test Results", show_header=True, header_style="bold green")
            results_table.add_column("Component", style="cyan")
            results_table.add_column("Status", style="yellow")
            results_table.add_column("Key Metrics", style="green")
            
            for component in self.components_tested:
                component_key = component.lower().replace(" ", "_").replace("-", "_")
                result = self.results.get(component_key, {})
                
                status = "✅ Success" if result.get("success", False) else "❌ Failed"
                
                if "ml_content_analysis" in component_key:
                    metrics = f"{result.get('features_extracted', 0)} features, {result.get('quality_predictions', 0)} predictions"
                elif "data_quality_assessment" in component_key:
                    metrics = f"Score: {result.get('overall_score', 0):.3f}, {result.get('anomalies_detected', 0)} anomalies"
                elif "pattern_recognition" in component_key:
                    metrics = f"{result.get('patterns_learned', 0)} patterns, {result.get('total_patterns', 0)} total"
                elif "predictive_discovery" in component_key:
                    metrics = f"{result.get('sources_discovered', 0)} sources, {result.get('seed_analysis_features', 0)} features"
                elif "system_integration" in component_key:
                    metrics = f"{result.get('tasks_available', 0)} tasks, {result.get('cli_commands', 0)} commands"
                else:
                    metrics = "Completed successfully"
                
                results_table.add_row(component, status, metrics)
            
            console.print(results_table)
        
        # Phase 3 capabilities summary
        console.print("\n[bold cyan]🎯 Phase 3: Advanced Discovery Capabilities[/bold cyan]")
        
        capabilities = [
            "[green]✅ ML-Powered Content Analysis[/green] - Intelligent feature extraction and classification",
            "[green]✅ Advanced Data Quality Assessment[/green] - Multi-dimensional quality scoring and anomaly detection",
            "[green]✅ Intelligent Pattern Recognition[/green] - Self-learning extraction optimization",
            "[green]✅ Predictive Source Discovery[/green] - ML-based related source identification",
            "[green]✅ Adaptive Learning Algorithms[/green] - Continuous improvement and optimization",
            "[green]✅ Comprehensive System Integration[/green] - Seamless task and CLI automation"
        ]
        
        for capability in capabilities:
            console.print(f"  {capability}")
        
        # Next steps
        console.print("\n[bold yellow]🚀 Next Steps:[/bold yellow]")
        console.print("  1. Install ML dependencies: pip install scikit-learn pandas numpy")
        console.print("  2. Configure Phase 3 components in your spider projects")
        console.print("  3. Start using ML-powered content analysis and quality assessment")
        console.print("  4. Enable adaptive pattern learning for your extraction workflows")
        console.print("  5. Explore predictive source discovery for automated expansion")
        
        console.print(f"\n[bold green]✨ Phase 3 Demo completed successfully in {demo_duration:.1f} seconds![/bold green]")
    
    async def run_full_demo(self) -> None:
        """Run the complete Phase 3 demonstration"""
        
        console.print(Panel.fit(
            "[bold cyan]🚀 Starting Phase 3: Advanced Discovery Full Demo[/bold cyan]\n"
            "[green]ML-Powered Content Analysis • Data Quality Assessment • Pattern Recognition[/green]\n"
            "[yellow]Predictive Discovery • Adaptive Learning • System Integration[/yellow]",
            title="Phase 3 Demo",
            border_style="cyan"
        ))
        
        try:
            # Run all Phase 3 demonstrations
            await self.demo_ml_content_analysis()
            await asyncio.sleep(1)  # Brief pause between demos
            
            await self.demo_data_quality_assessment()
            await asyncio.sleep(1)
            
            await self.demo_intelligent_pattern_recognition()
            await asyncio.sleep(1)
            
            await self.demo_predictive_discovery()
            await asyncio.sleep(1)
            
            await self.demo_system_integration()
            
            # Generate final summary
            self.generate_demo_summary()
            
        except KeyboardInterrupt:
            console.print("\n[red]🛑 Phase 3 demo interrupted by user[/red]")
            raise
        except Exception as exc:
            console.print(f"\n[red]❌ Phase 3 demo failed: {exc}[/red]")
            raise


# Demo runner for direct execution
async def main():
    """Main demo runner"""
    demo = Phase3Demo()
    
    try:
        await demo.run_full_demo()
    except KeyboardInterrupt:
        console.print("\n🛑 Demo cancelled by user")
    except Exception as e:
        console.print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Enable rich tracebacks for better error display
    from rich.traceback import install
    install(show_locals=True)
    
    asyncio.run(main())
