"""Phase 3: Advanced Discovery CLI Commands - ML-Powered Intelligent Automation"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

# Console for rich output
console = Console()


@click.group(name="phase3")
@click.pass_context
def phase3_cli(ctx: click.Context) -> None:
    """Phase 3: Advanced Discovery Features - ML-Powered Intelligence"""
    
    # Display Phase 3 banner
    console.print(Panel.fit(
        "[bold cyan]Phase 3: Advanced Discovery Features[/bold cyan]\n"
        "[green]ML-Powered Content Analysis • Data Quality Assessment • Pattern Recognition[/green]\n"
        "[yellow]Predictive Discovery • Intelligent Optimization • Adaptive Learning[/yellow]",
        border_style="cyan"
    ))


@phase3_cli.command()
@click.argument("url")
@click.option("--html-file", type=click.Path(exists=True), help="HTML file to analyze instead of fetching URL")
@click.option("--output", "-o", type=click.Path(), help="Output file for analysis results")
@click.option("--detailed", is_flag=True, help="Show detailed feature analysis")
def analyze_content(url: str, html_file: Optional[str], output: Optional[str], detailed: bool) -> None:
    """Analyze content using ML-powered content analysis"""
    
    console.print(f"[cyan]Analyzing content for: {url}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing content...", total=None)
        
        try:
            # Import Phase 3 components
            from ..discovery.ml_content_analysis import content_analyzer
            
            if content_analyzer is None:
                console.print("[red]❌ ML content analyzer not available[/red]")
                return
            
            # Get HTML content
            if html_file:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                import aiohttp
                
                async def fetch_content():
                    timeout = aiohttp.ClientTimeout(total=30)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                return await response.text()
                            else:
                                raise Exception(f"Failed to fetch URL: HTTP {response.status}")
                
                html_content = asyncio.run(fetch_content())
            
            # Analyze content
            async def analyze():
                features = await content_analyzer.analyze_content(url, html_content)
                quality_predictions = await content_analyzer.predict_content_quality(features)
                return features, quality_predictions
            
            features, quality_predictions = asyncio.run(analyze())
            progress.update(task, description="Analysis complete!")
            
        except Exception as exc:
            progress.update(task, description="Analysis failed!")
            console.print(f"[red]❌ Analysis failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Content Analysis Complete[/green]")
    
    # Create results table
    table = Table(title="Content Features", show_header=True, header_style="bold magenta")
    table.add_column("Feature", style="cyan")
    table.add_column("Value", style="yellow")
    
    # Basic features
    table.add_row("URL", features.url)
    table.add_row("Content Type", features.content_type)
    table.add_row("Language", features.language)
    table.add_row("Word Count", str(features.word_count))
    table.add_row("Link Count", str(features.link_count))
    table.add_row("Image Count", str(features.image_count))
    table.add_row("Form Count", str(features.form_count))
    table.add_row("Table Count", str(features.table_count))
    table.add_row("Readability Score", f"{features.readability_score:.2f}")
    table.add_row("Content Density", f"{features.content_density:.2f}")
    
    console.print(table)
    
    # Quality predictions
    if quality_predictions:
        quality_table = Table(title="Quality Predictions", show_header=True, header_style="bold green")
        quality_table.add_column("Metric", style="cyan")
        quality_table.add_column("Score", style="yellow")
        quality_table.add_column("Confidence", style="magenta")
        
        for metric, data in quality_predictions.items():
            if isinstance(data, dict):
                score = data.get('score', 'N/A')
                confidence = data.get('confidence', 'N/A')
                quality_table.add_row(
                    metric.replace('_', ' ').title(),
                    f"{score:.3f}" if isinstance(score, float) else str(score),
                    f"{confidence:.3f}" if isinstance(confidence, float) else str(confidence)
                )
            else:
                quality_table.add_row(metric.replace('_', ' ').title(), str(data), "N/A")
        
        console.print(quality_table)
    
    # Detailed analysis
    if detailed:
        console.print("\n[bold]Detailed Feature Analysis:[/bold]")
        
        # Entity analysis
        if features.entities:
            entity_table = Table(title="Named Entities", show_header=True, header_style="bold blue")
            entity_table.add_column("Entity", style="cyan")
            entity_table.add_column("Type", style="yellow")
            entity_table.add_column("Count", style="green")
            
            for entity_type, entities in features.entities.items():
                if isinstance(entities, dict):
                    for entity, count in entities.items():
                        entity_table.add_row(str(entity), entity_type, str(count))
                elif isinstance(entities, list):
                    for entity in entities:
                        entity_table.add_row(str(entity), entity_type, "1")
            
            console.print(entity_table)
        
        # Topic analysis
        if features.topics:
            topic_table = Table(title="Topic Analysis", show_header=True, header_style="bold purple")
            topic_table.add_column("Topic", style="cyan")
            topic_table.add_column("Score", style="yellow")
            
            for topic, score in features.topics.items():
                topic_table.add_row(topic, f"{score:.3f}")
            
            console.print(topic_table)
    
    # Save results if requested
    if output:
        results = {
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'url': url,
            'features': features.to_dict(),
            'quality_predictions': quality_predictions
        }
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]💾 Results saved to: {output}[/green]")


@phase3_cli.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--source-url", help="Source URL of the data")
@click.option("--format", "data_format", type=click.Choice(["json", "csv", "raw"]), default="json", help="Data format")
@click.option("--output", "-o", type=click.Path(), help="Output file for quality report")
@click.option("--detailed", is_flag=True, help="Show detailed quality metrics")
def assess_quality(data_file: str, source_url: Optional[str], data_format: str, output: Optional[str], detailed: bool) -> None:
    """Assess data quality using advanced ML-powered analysis"""
    
    console.print(f"[cyan]Assessing quality of: {data_file}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Loading data...", total=None)
        
        try:
            # Load data
            if data_format == "json":
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif data_format == "csv":
                import pandas as pd
                df = pd.read_csv(data_file)
                data = df.to_dict('records')
            else:  # raw
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = f.read()
            
            progress.update(task, description="Assessing quality...")
            
            # Import Phase 3 components
            from ..discovery.data_quality_assessment import quality_assessor
            
            # Assess quality
            async def assess():
                metrics = await quality_assessor.assess_data_quality(data, source_url or "")
                report = quality_assessor.generate_quality_report(metrics)
                return metrics, report
            
            metrics, report = asyncio.run(assess())
            progress.update(task, description="Quality assessment complete!")
            
        except Exception as exc:
            progress.update(task, description="Assessment failed!")
            console.print(f"[red]❌ Quality assessment failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Data Quality Assessment Complete[/green]")
    
    # Overall quality score
    overall_score = metrics.overall_quality_score
    score_color = "green" if overall_score >= 0.8 else "yellow" if overall_score >= 0.6 else "red"
    
    console.print(f"\n[bold]Overall Quality Score: [{score_color}]{overall_score:.3f}[/{score_color}][/bold]")
    
    # Quality metrics table
    quality_table = Table(title="Quality Metrics", show_header=True, header_style="bold magenta")
    quality_table.add_column("Metric", style="cyan")
    quality_table.add_column("Score", style="yellow")
    quality_table.add_column("Details", style="white")
    
    quality_table.add_row("Completeness", f"{metrics.completeness_score:.3f}", f"{metrics.completeness_details}")
    quality_table.add_row("Consistency", f"{metrics.consistency_score:.3f}", f"{metrics.consistency_details}")
    quality_table.add_row("Validity", f"{metrics.validity_score:.3f}", f"{metrics.validity_details}")
    quality_table.add_row("Accuracy", f"{metrics.accuracy_score:.3f}", f"{metrics.accuracy_details}")
    quality_table.add_row("Uniqueness", f"{metrics.uniqueness_score:.3f}", f"{metrics.uniqueness_details}")
    quality_table.add_row("Timeliness", f"{metrics.timeliness_score:.3f}", f"{metrics.timeliness_details}")
    
    console.print(quality_table)
    
    # Display quality report
    console.print(f"\n[bold]Quality Report:[/bold]")
    console.print(report)
    
    # Anomalies detected
    if metrics.anomalies_detected:
        anomaly_table = Table(title="Anomalies Detected", show_header=True, header_style="bold red")
        anomaly_table.add_column("Type", style="red")
        anomaly_table.add_column("Description", style="yellow")
        anomaly_table.add_column("Severity", style="magenta")
        
        for anomaly in metrics.anomalies_detected:
            if isinstance(anomaly, dict):
                anomaly_table.add_row(
                    anomaly.get('type', 'Unknown'),
                    anomaly.get('description', 'No description'),
                    anomaly.get('severity', 'Medium')
                )
            else:
                anomaly_table.add_row("General", str(anomaly), "Medium")
        
        console.print(anomaly_table)
    
    # Detailed metrics
    if detailed:
        console.print("\n[bold]Detailed Quality Analysis:[/bold]")
        
        # Statistical overview
        if hasattr(metrics, 'statistical_overview'):
            stats_table = Table(title="Statistical Overview", show_header=True, header_style="bold blue")
            stats_table.add_column("Statistic", style="cyan")
            stats_table.add_column("Value", style="yellow")
            
            for stat, value in metrics.statistical_overview.items():
                stats_table.add_row(stat, str(value))
            
            console.print(stats_table)
    
    # Save results if requested
    if output:
        results = {
            'assessment_timestamp': datetime.utcnow().isoformat(),
            'data_source': data_file,
            'source_url': source_url,
            'metrics': metrics.to_dict(),
            'quality_report': report
        }
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]💾 Results saved to: {output}[/green]")


@phase3_cli.command()
@click.argument("session_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for learned patterns")
def learn_patterns(session_file: str, output: Optional[str]) -> None:
    """Learn patterns from spider execution session data"""
    
    console.print(f"[cyan]Learning patterns from: {session_file}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Loading session data...", total=None)
        
        try:
            # Load session data
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            progress.update(task, description="Learning patterns...")
            
            # Import Phase 3 components
            from ..discovery.intelligent_pattern_recognition import pattern_recognizer, LearningSession
            
            # Create learning session
            session = LearningSession(
                session_id=session_data.get('session_id', str(time.time())),
                spider_name=session_data['spider_name'],
                target_url=session_data['target_url'],
                start_time=datetime.fromisoformat(session_data['start_time']),
                end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                duration=session_data.get('duration', 0.0),
                records_extracted=session_data.get('records_extracted', 0),
                errors_encountered=session_data.get('errors_encountered', 0),
                data_quality_score=session_data.get('data_quality_score', 0.0),
                successful_selectors=session_data.get('successful_selectors', {}),
                failed_selectors=session_data.get('failed_selectors', []),
                adaptations_made=session_data.get('adaptations_made', []),
                page_structure_hash=session_data.get('page_structure_hash', ''),
                response_characteristics=session_data.get('response_characteristics', {})
            )
            
            # Learn from session
            async def learn():
                return await pattern_recognizer.learn_from_session(session)
            
            learned_patterns = asyncio.run(learn())
            progress.update(task, description="Pattern learning complete!")
            
        except Exception as exc:
            progress.update(task, description="Pattern learning failed!")
            console.print(f"[red]❌ Pattern learning failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Pattern Learning Complete[/green]")
    
    console.print(f"[bold]Learned {len(learned_patterns)} patterns from session[/bold]")
    
    if learned_patterns:
        pattern_table = Table(title="Learned Patterns", show_header=True, header_style="bold purple")
        pattern_table.add_column("Pattern ID", style="cyan")
        pattern_table.add_column("Type", style="yellow")
        pattern_table.add_column("Confidence", style="green")
        pattern_table.add_column("Usage Count", style="magenta")
        
        for pattern in learned_patterns:
            pattern_table.add_row(
                pattern.pattern_id,
                pattern.pattern_type,
                f"{pattern.confidence:.3f}",
                str(pattern.usage_count)
            )
        
        console.print(pattern_table)
        
        # Pattern statistics
        stats = pattern_recognizer.get_pattern_statistics()
        
        stats_table = Table(title="Pattern Statistics", show_header=True, header_style="bold blue")
        stats_table.add_column("Statistic", style="cyan")
        stats_table.add_column("Value", style="yellow")
        
        for stat, value in stats.items():
            stats_table.add_row(stat.replace('_', ' ').title(), str(value))
        
        console.print(stats_table)
        
        # Save results if requested
        if output:
            results = {
                'learning_timestamp': datetime.utcnow().isoformat(),
                'session_source': session_file,
                'patterns_learned': len(learned_patterns),
                'learned_patterns': [
                    {
                        'pattern_id': p.pattern_id,
                        'pattern_type': p.pattern_type,
                        'confidence': p.confidence,
                        'usage_count': p.usage_count,
                        'selectors': p.selectors,
                        'success_rate': p.success_rate
                    } for p in learned_patterns
                ],
                'statistics': stats
            }
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]💾 Results saved to: {output}[/green]")


@phase3_cli.command()
@click.argument("seed_url")
@click.option("--max-sources", type=int, default=10, help="Maximum number of sources to discover")
@click.option("--output", "-o", type=click.Path(), help="Output file for discovered sources")
def discover_sources(seed_url: str, max_sources: int, output: Optional[str]) -> None:
    """Discover related sources using predictive ML analysis"""
    
    console.print(f"[cyan]Discovering sources from: {seed_url}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing seed source...", total=None)
        
        try:
            # Import Phase 3 components
            from ..discovery.ml_content_analysis import content_analyzer, predictive_discovery
            import aiohttp
            
            if not content_analyzer or not predictive_discovery:
                console.print("[red]❌ ML predictive discovery not available[/red]")
                return
            
            # Analyze seed URL and discover sources
            async def discover():
                # Fetch and analyze seed URL
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(seed_url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            content_features = await content_analyzer.analyze_content(seed_url, html_content)
                        else:
                            raise Exception(f"Failed to fetch seed URL: HTTP {response.status}")
                
                progress.update(task, description="Discovering related sources...")
                
                # Discover related sources
                discovered_sources = await predictive_discovery.discover_related_sources(
                    seed_url, content_features, max_sources
                )
                
                return content_features, discovered_sources
            
            content_features, discovered_sources = asyncio.run(discover())
            progress.update(task, description="Source discovery complete!")
            
        except Exception as exc:
            progress.update(task, description="Source discovery failed!")
            console.print(f"[red]❌ Source discovery failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Source Discovery Complete[/green]")
    
    console.print(f"[bold]Discovered {len(discovered_sources)} related sources[/bold]")
    
    if discovered_sources:
        source_table = Table(title="Discovered Sources", show_header=True, header_style="bold green")
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
        
        # Save results if requested
        if output:
            results = {
                'discovery_timestamp': datetime.utcnow().isoformat(),
                'seed_url': seed_url,
                'max_sources_requested': max_sources,
                'sources_discovered': len(discovered_sources),
                'seed_analysis': content_features.to_dict(),
                'discovered_sources': discovered_sources
            }
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]💾 Results saved to: {output}[/green]")


@phase3_cli.command()
@click.argument("url")
@click.argument("selectors", nargs=-1, required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for optimization results")
def optimize_selectors(url: str, selectors: tuple, output: Optional[str]) -> None:
    """Optimize extraction selectors using learned patterns"""
    
    selector_list = list(selectors)
    console.print(f"[cyan]Optimizing {len(selector_list)} selectors for: {url}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing content...", total=None)
        
        try:
            # Import Phase 3 components
            from ..discovery.intelligent_pattern_recognition import pattern_recognizer
            from ..discovery.ml_content_analysis import content_analyzer
            import aiohttp
            
            # Analyze content and optimize selectors
            async def optimize():
                # Fetch and analyze content
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            content_features = await content_analyzer.analyze_content(url, html_content)
                        else:
                            raise Exception(f"Failed to fetch URL: HTTP {response.status}")
                
                progress.update(task, description="Getting strategy recommendation...")
                
                # Get extraction strategy recommendation
                strategy_recommendation = await pattern_recognizer.recommend_extraction_strategy(
                    url, content_features
                )
                
                progress.update(task, description="Optimizing selectors...")
                
                # Optimize selectors
                optimized_selectors = await pattern_recognizer.optimize_selectors(
                    selector_list, url, content_features
                )
                
                return content_features, strategy_recommendation, optimized_selectors
            
            content_features, strategy_recommendation, optimized_selectors = asyncio.run(optimize())
            progress.update(task, description="Optimization complete!")
            
        except Exception as exc:
            progress.update(task, description="Optimization failed!")
            console.print(f"[red]❌ Optimization failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Selector Optimization Complete[/green]")
    
    # Strategy recommendation
    console.print(f"[bold]Recommended Strategy:[/bold] {strategy_recommendation}")
    
    # Selector comparison
    comparison_table = Table(title="Selector Optimization", show_header=True, header_style="bold blue")
    comparison_table.add_column("Original Selector", style="red")
    comparison_table.add_column("Optimized Selector", style="green")
    comparison_table.add_column("Improvement", style="yellow")
    
    for i, original in enumerate(selector_list):
        optimized = optimized_selectors[i] if i < len(optimized_selectors) else original
        improvement = "✅ Optimized" if optimized != original else "ℹ️ No change"
        comparison_table.add_row(original, optimized, improvement)
    
    console.print(comparison_table)
    
    # Save results if requested
    if output:
        results = {
            'optimization_timestamp': datetime.utcnow().isoformat(),
            'url': url,
            'original_selectors': selector_list,
            'optimized_selectors': optimized_selectors,
            'strategy_recommendation': strategy_recommendation,
            'content_analysis': content_features.to_dict()
        }
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]💾 Results saved to: {output}[/green]")


@phase3_cli.command()
def run_learning_cycle() -> None:
    """Run adaptive learning cycle to improve pattern recognition"""
    
    console.print("[cyan]Running adaptive learning cycle...[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Starting learning cycle...", total=None)
        
        try:
            # Import Phase 3 components
            from ..discovery.intelligent_pattern_recognition import pattern_recognizer
            
            # Get statistics before learning cycle
            stats_before = pattern_recognizer.get_pattern_statistics()
            
            progress.update(task, description="Running adaptive learning...")
            
            # Run learning cycle
            async def learn():
                await pattern_recognizer.adaptive_learning_cycle()
                return pattern_recognizer.get_pattern_statistics()
            
            stats_after = asyncio.run(learn())
            progress.update(task, description="Learning cycle complete!")
            
        except Exception as exc:
            progress.update(task, description="Learning cycle failed!")
            console.print(f"[red]❌ Learning cycle failed: {exc}[/red]")
            return
    
    # Display results
    console.print("\n[green]✅ Adaptive Learning Cycle Complete[/green]")
    
    # Statistics comparison
    stats_table = Table(title="Learning Cycle Results", show_header=True, header_style="bold purple")
    stats_table.add_column("Statistic", style="cyan")
    stats_table.add_column("Before", style="yellow")
    stats_table.add_column("After", style="green")
    stats_table.add_column("Change", style="magenta")
    
    for stat, before_value in stats_before.items():
        after_value = stats_after.get(stat, 0)
        change = after_value - before_value if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)) else "N/A"
        
        stats_table.add_row(
            stat.replace('_', ' ').title(),
            str(before_value),
            str(after_value),
            f"+{change}" if isinstance(change, (int, float)) and change > 0 else str(change)
        )
    
    console.print(stats_table)
    
    # Learning summary
    patterns_change = stats_after.get('total_patterns', 0) - stats_before.get('total_patterns', 0)
    if patterns_change > 0:
        console.print(f"[green]✨ {patterns_change} new patterns learned![/green]")
    elif patterns_change < 0:
        console.print(f"[yellow]🔄 {abs(patterns_change)} patterns refined/removed[/yellow]")
    else:
        console.print("[blue]ℹ️ No new patterns learned - existing patterns optimized[/blue]")


@phase3_cli.command()
@click.option("--days", type=int, default=30, help="Number of days to include in report")
@click.option("--output", "-o", type=click.Path(), help="Output file for insights report")
def generate_insights(days: int, output: Optional[str]) -> None:
    """Generate comprehensive ML insights report"""
    
    console.print(f"[cyan]Generating ML insights report for last {days} days...[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Collecting insights...", total=None)
        
        try:
            # Import Phase 3 components
            from ..discovery.intelligent_pattern_recognition import pattern_recognizer
            from ..discovery.ml_content_analysis import content_analyzer
            from ..discovery.data_quality_assessment import quality_assessor
            
            # Collect insights
            progress.update(task, description="Analyzing patterns...")
            pattern_stats = pattern_recognizer.get_pattern_statistics()
            
            progress.update(task, description="Analyzing content...")
            analysis_stats = content_analyzer.get_analysis_statistics() if content_analyzer else {}
            
            progress.update(task, description="Analyzing quality trends...")
            quality_trends = quality_assessor.get_quality_trends(days=days)
            
            progress.update(task, description="Generating report...")
            
            # Compile insights
            insights = {
                'report_generated_at': datetime.utcnow().isoformat(),
                'period_days': days,
                'pattern_recognition': {
                    'statistics': pattern_stats,
                    'status': 'Active' if pattern_stats.get('total_patterns', 0) > 0 else 'Inactive'
                },
                'content_analysis': {
                    'statistics': analysis_stats,
                    'status': 'Active' if analysis_stats.get('total_analyzed', 0) > 0 else 'Inactive'
                },
                'quality_assessment': {
                    'trends': quality_trends,
                    'status': 'Active' if 'error' not in quality_trends else 'Error'
                }
            }
            
        except Exception as exc:
            progress.update(task, description="Report generation failed!")
            console.print(f"[red]❌ Report generation failed: {exc}[/red]")
            return
        
        progress.update(task, description="Report complete!")
    
    # Display results
    console.print("\n[green]✅ ML Insights Report Generated[/green]")
    
    # System overview
    overview_table = Table(title="Phase 3 System Overview", show_header=True, header_style="bold cyan")
    overview_table.add_column("Component", style="cyan")
    overview_table.add_column("Status", style="yellow")
    overview_table.add_column("Key Metrics", style="green")
    
    # Pattern recognition status
    pr_status = insights['pattern_recognition']['status']
    pr_metrics = f"{pattern_stats.get('total_patterns', 0)} patterns, {pattern_stats.get('learning_sessions', 0)} sessions"
    overview_table.add_row("Pattern Recognition", pr_status, pr_metrics)
    
    # Content analysis status
    ca_status = insights['content_analysis']['status']
    ca_metrics = f"{analysis_stats.get('total_analyzed', 0)} analyses, {analysis_stats.get('avg_quality', 0):.2f} avg quality"
    overview_table.add_row("Content Analysis", ca_status, ca_metrics)
    
    # Quality assessment status
    qa_status = insights['quality_assessment']['status']
    qa_metrics = "Trends available" if qa_status == 'Active' else "No data"
    overview_table.add_row("Quality Assessment", qa_status, qa_metrics)
    
    console.print(overview_table)
    
    # Detailed statistics
    if pattern_stats:
        pattern_table = Table(title="Pattern Recognition Details", show_header=True, header_style="bold purple")
        pattern_table.add_column("Metric", style="cyan")
        pattern_table.add_column("Value", style="yellow")
        
        for metric, value in pattern_stats.items():
            pattern_table.add_row(metric.replace('_', ' ').title(), str(value))
        
        console.print(pattern_table)
    
    # Save report if requested
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]💾 Insights report saved to: {output}[/green]")


@phase3_cli.command()
def status() -> None:
    """Show Phase 3 system status and health"""
    
    console.print("[cyan]Checking Phase 3 system status...[/cyan]")
    
    try:
        # Import Phase 3 components
        from ..discovery.ml_content_analysis import content_analyzer
        from ..discovery.data_quality_assessment import quality_assessor  
        from ..discovery.intelligent_pattern_recognition import pattern_recognizer
        
        # System health panel
        health_items = []
        
        # Content analyzer
        if content_analyzer is not None:
            health_items.append("[green]✅ ML Content Analyzer[/green] - Ready")
        else:
            health_items.append("[red]❌ ML Content Analyzer[/red] - Not available")
        
        # Quality assessor
        if quality_assessor is not None:
            health_items.append("[green]✅ Data Quality Assessor[/green] - Ready")
        else:
            health_items.append("[red]❌ Data Quality Assessor[/red] - Not available")
        
        # Pattern recognizer
        if pattern_recognizer is not None:
            health_items.append("[green]✅ Pattern Recognizer[/green] - Ready")
            
            # Get pattern statistics
            stats = pattern_recognizer.get_pattern_statistics()
            health_items.append(f"  • Patterns: {stats.get('total_patterns', 0)}")
            health_items.append(f"  • Learning Sessions: {stats.get('learning_sessions', 0)}")
        else:
            health_items.append("[red]❌ Pattern Recognizer[/red] - Not available")
        
        # ML dependencies
        try:
            import sklearn
            health_items.append("[green]✅ scikit-learn[/green] - Available")
        except ImportError:
            health_items.append("[yellow]⚠️ scikit-learn[/yellow] - Not available (fallback mode)")
        
        try:
            import pandas
            health_items.append("[green]✅ pandas[/green] - Available")
        except ImportError:
            health_items.append("[red]❌ pandas[/red] - Required for data processing")
        
        try:
            import numpy
            health_items.append("[green]✅ numpy[/green] - Available")
        except ImportError:
            health_items.append("[red]❌ numpy[/red] - Required for ML operations")
        
        # Display health status
        console.print(Panel(
            "\n".join(health_items),
            title="[bold cyan]Phase 3: Advanced Discovery System Health[/bold cyan]",
            border_style="cyan"
        ))
        
    except Exception as exc:
        console.print(f"[red]❌ Status check failed: {exc}[/red]")


if __name__ == "__main__":
    # Enable rich tracebacks for better error display
    from rich.traceback import install
    install(show_locals=True)
    
    phase3_cli()
