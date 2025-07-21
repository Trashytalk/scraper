"""
Analysis CLI commands for entity resolution, relationship mapping, enrichment, and event detection
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import click
import pandas as pd
from tabulate import tabulate

from ..analysis import (
    AdvancedEntityResolver,
    EntityRelationshipMapper,
    DataEnrichmentEngine,
    BusinessEventDetector,
    AnalysisOrchestrator
)
from ..analysis.orchestrator import AnalysisRequest
from ..db.repository import get_repository

logger = logging.getLogger(__name__)


def get_analysis_config() -> Dict[str, Any]:
    """Get analysis configuration"""
    return {
        'entity_resolution': {
            'similarity_threshold': 0.7,
            'clustering_eps': 0.3,
            'min_samples': 2,
            'max_entities': 10000
        },
        'relationship_mapping': {
            'confidence_threshold': 0.6,
            'max_relationships': 5000,
            'include_weak_relationships': False
        },
        'enrichment': {
            'cache_ttl_hours': 24,
            'max_concurrent_requests': 10,
            'max_cost_per_request': 1.0
        },
        'event_detection': {
            'deduplication_window_hours': 24,
            'min_confidence': 0.7,
            'max_events_per_scan': 1000
        }
    }


@click.group(name='analysis')
def analysis_cli():
    """Analysis and cross-referencing commands"""
    pass


@analysis_cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file containing entities (JSON or CSV)')
@click.option('--output-file', '-o', type=click.Path(), 
              help='Output file for results (default: stdout)')
@click.option('--analysis-types', '-t', multiple=True,
              default=['entity_resolution', 'relationship_mapping', 'enrichment', 'event_detection'],
              help='Analysis types to run')
@click.option('--confidence-threshold', '-c', default=0.7, type=float,
              help='Minimum confidence threshold')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']),
              default='json', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def comprehensive(input_file, output_file, analysis_types, confidence_threshold, format, verbose):
    """Run comprehensive analysis pipeline"""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    try:
        # Load entities from input file
        entities = load_entities_from_file(input_file)
        click.echo(f"Loaded {len(entities)} entities from {input_file}")
        
        # Create analysis request
        request_id = f"cli_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        analysis_request = AnalysisRequest(
            request_id=request_id,
            entities=entities,
            analysis_types=list(analysis_types),
            confidence_threshold=confidence_threshold
        )
        
        # Run analysis
        config = get_analysis_config()
        orchestrator = AnalysisOrchestrator(config)
        
        with click.progressbar(length=100, label='Running analysis') as bar:
            result = asyncio.run(orchestrator.run_comprehensive_analysis(analysis_request))
            bar.update(100)
        
        # Output results
        output_results(result, output_file, format, verbose)
        
        # Print summary
        click.echo(f"\nAnalysis completed successfully:")
        click.echo(f"  - Request ID: {result.request_id}")
        click.echo(f"  - Duration: {result.metrics.get('duration_seconds', 0):.2f} seconds")
        click.echo(f"  - Entities processed: {result.metrics.get('entities_processed', 0)}")
        click.echo(f"  - Risk level: {result.summary.get('risk_assessment', 'UNKNOWN')}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file containing entities')
@click.option('--output-file', '-o', type=click.Path(),
              help='Output file for entity clusters')
@click.option('--similarity-threshold', '-s', default=0.7, type=float,
              help='Similarity threshold for clustering')
@click.option('--clustering-method', '-m', type=click.Choice(['dbscan', 'hierarchical']),
              default='dbscan', help='Clustering algorithm')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']),
              default='table', help='Output format')
@click.option('--show-matrix', is_flag=True, help='Show similarity matrix')
def resolve_entities(input_file, output_file, similarity_threshold, clustering_method, format, show_matrix):
    """Resolve entity duplicates using fuzzy matching"""
    try:
        entities = load_entities_from_file(input_file)
        click.echo(f"Loaded {len(entities)} entities for resolution")
        
        config = get_analysis_config()
        config['entity_resolution']['similarity_threshold'] = similarity_threshold
        
        resolver = AdvancedEntityResolver(config['entity_resolution'])
        
        with click.progressbar(length=100, label='Resolving entities') as bar:
            clusters = resolver.resolve_entities(entities)
            bar.update(100)
        
        # Output results
        if format == 'table':
            output_entity_clusters_table(clusters)
        elif format == 'json':
            output_data = {'clusters': clusters, 'total_entities': len(entities)}
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(output_data, f, indent=2, default=str)
            else:
                click.echo(json.dumps(output_data, indent=2, default=str))
        elif format == 'csv':
            output_entity_clusters_csv(clusters, output_file)
        
        # Show similarity matrix if requested
        if show_matrix:
            click.echo("\nSimilarity Matrix:")
            matrix = resolver.calculate_similarity_matrix(entities)
            df = pd.DataFrame(matrix)
            click.echo(df.to_string())
        
        # Summary
        duplicate_ratio = 1.0 - (len(clusters) / len(entities)) if entities else 0.0
        click.echo(f"\nResolution Summary:")
        click.echo(f"  - Total entities: {len(entities)}")
        click.echo(f"  - Unique clusters: {len(clusters)}")
        click.echo(f"  - Duplicate ratio: {duplicate_ratio:.2%}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file containing entities')
@click.option('--output-file', '-o', type=click.Path(),
              help='Output file for relationships')
@click.option('--relationship-types', '-r', multiple=True,
              default=['officer', 'ownership', 'address', 'contact'],
              help='Relationship types to extract')
@click.option('--confidence-threshold', '-c', default=0.6, type=float,
              help='Minimum confidence threshold')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']),
              default='table', help='Output format')
@click.option('--build-graph', is_flag=True, help='Build and analyze network graph')
def map_relationships(input_file, output_file, relationship_types, confidence_threshold, format, build_graph):
    """Extract and map entity relationships"""
    try:
        entities = load_entities_from_file(input_file)
        click.echo(f"Loaded {len(entities)} entities for relationship mapping")
        
        config = get_analysis_config()
        config['relationship_mapping']['confidence_threshold'] = confidence_threshold
        
        mapper = EntityRelationshipMapper(config['relationship_mapping'])
        
        with click.progressbar(length=100, label='Mapping relationships') as bar:
            relationships = mapper.extract_relationships(entities, list(relationship_types))
            bar.update(100)
        
        # Filter by confidence
        filtered_relationships = [r for r in relationships if r.confidence_score >= confidence_threshold]
        
        # Output results
        if format == 'table':
            output_relationships_table(filtered_relationships)
        elif format == 'json':
            relationship_data = []
            for rel in filtered_relationships:
                relationship_data.append({
                    'source_entity': rel.source_entity,
                    'target_entity': rel.target_entity,
                    'relationship_type': rel.relationship_type,
                    'confidence_score': rel.confidence_score,
                    'metadata': rel.metadata
                })
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(relationship_data, f, indent=2, default=str)
            else:
                click.echo(json.dumps(relationship_data, indent=2, default=str))
        elif format == 'csv':
            output_relationships_csv(filtered_relationships, output_file)
        
        # Build network graph if requested
        if build_graph and filtered_relationships:
            click.echo("\nBuilding network graph...")
            graph_metrics = mapper.build_network_graph(filtered_relationships)
            
            click.echo("Network Metrics:")
            for metric, value in graph_metrics.items():
                click.echo(f"  - {metric}: {value}")
        
        # Summary
        type_counts = {}
        for rel in filtered_relationships:
            rel_type = rel.relationship_type
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        click.echo(f"\nRelationship Mapping Summary:")
        click.echo(f"  - Total relationships: {len(filtered_relationships)}")
        click.echo(f"  - Relationship types: {list(type_counts.keys())}")
        for rel_type, count in type_counts.items():
            click.echo(f"    - {rel_type}: {count}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file containing entities')
@click.option('--output-file', '-o', type=click.Path(),
              help='Output file for enrichment results')
@click.option('--sources', '-s', multiple=True,
              default=['sanctions', 'contracts', 'financial'],
              help='Enrichment sources to use')
@click.option('--max-cost', default=10.0, type=float,
              help='Maximum cost for enrichment requests')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']),
              default='table', help='Output format')
def enrich(input_file, output_file, sources, max_cost, format):
    """Enrich entities with external data sources"""
    try:
        entities = load_entities_from_file(input_file)
        click.echo(f"Loaded {len(entities)} entities for enrichment")
        
        config = get_analysis_config()
        enrichment_engine = DataEnrichmentEngine(config['enrichment'])
        
        with click.progressbar(length=100, label='Enriching entities') as bar:
            enrichments = asyncio.run(enrichment_engine.enrich_entities(entities, list(sources)))
            bar.update(100)
        
        # Calculate total cost
        total_cost = sum(e.cost for e in enrichments)
        if total_cost > max_cost:
            click.echo(f"Warning: Total cost ${total_cost:.2f} exceeds maximum ${max_cost:.2f}")
        
        # Output results
        if format == 'table':
            output_enrichments_table(enrichments)
        elif format == 'json':
            enrichment_data = []
            for enrich in enrichments:
                enrichment_data.append({
                    'entity_id': enrich.entity_id,
                    'source_name': enrich.source_name,
                    'enrichment_type': enrich.enrichment_type,
                    'data': enrich.data,
                    'confidence_score': enrich.confidence_score,
                    'cost': enrich.cost
                })
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(enrichment_data, f, indent=2, default=str)
            else:
                click.echo(json.dumps(enrichment_data, indent=2, default=str))
        elif format == 'csv':
            output_enrichments_csv(enrichments, output_file)
        
        # Summary
        source_counts = {}
        for enrich in enrichments:
            source = enrich.source_name
            source_counts[source] = source_counts.get(source, 0) + 1
        
        click.echo(f"\nEnrichment Summary:")
        click.echo(f"  - Total enrichments: {len(enrichments)}")
        click.echo(f"  - Total cost: ${total_cost:.2f}")
        click.echo(f"  - Sources used: {list(source_counts.keys())}")
        
        # Show high-risk findings
        high_risk_enrichments = [e for e in enrichments if 'sanctioned' in str(e.data).lower()]
        if high_risk_enrichments:
            click.echo(f"\n⚠️  HIGH RISK FINDINGS:")
            for enrich in high_risk_enrichments:
                click.echo(f"  - {enrich.entity_id}: {enrich.source_name}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file containing data sources')
@click.option('--output-file', '-o', type=click.Path(),
              help='Output file for detected events')
@click.option('--entity-names', '-e', multiple=True,
              help='Entity names to focus detection on')
@click.option('--severity-filter', type=click.Choice(['low', 'medium', 'high', 'critical']),
              help='Filter events by severity')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']),
              default='table', help='Output format')
def detect_events(input_file, output_file, entity_names, severity_filter, format):
    """Detect business events from data sources"""
    try:
        # Load data sources
        with open(input_file, 'r') as f:
            data_sources = json.load(f)
        
        click.echo(f"Loaded {len(data_sources)} data sources for event detection")
        
        config = get_analysis_config()
        detector = BusinessEventDetector(config['event_detection'])
        
        with click.progressbar(length=100, label='Detecting events') as bar:
            events = asyncio.run(detector.detect_events(data_sources, list(entity_names) if entity_names else None))
            bar.update(100)
        
        # Apply severity filter
        if severity_filter:
            events = [e for e in events if e.severity.value == severity_filter]
        
        # Output results
        if format == 'table':
            output_events_table(events)
        elif format == 'json':
            event_data = []
            for event in events:
                event_data.append({
                    'event_id': event.event_id,
                    'entity_id': event.entity_id,
                    'event_type': event.event_type,
                    'category': event.category.value,
                    'severity': event.severity.value,
                    'title': event.title,
                    'confidence_score': event.confidence_score
                })
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(event_data, f, indent=2, default=str)
            else:
                click.echo(json.dumps(event_data, indent=2, default=str))
        elif format == 'csv':
            output_events_csv(events, output_file)
        
        # Summary
        severity_counts = {}
        category_counts = {}
        for event in events:
            severity = event.severity.value
            category = event.category.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        click.echo(f"\nEvent Detection Summary:")
        click.echo(f"  - Total events: {len(events)}")
        click.echo(f"  - Severity distribution: {severity_counts}")
        click.echo(f"  - Category distribution: {category_counts}")
        
        # Show critical/high severity events
        critical_events = [e for e in events if e.severity.value in ['critical', 'high']]
        if critical_events:
            click.echo(f"\n🚨 HIGH PRIORITY EVENTS:")
            for event in critical_events[:5]:  # Show top 5
                click.echo(f"  - {event.title} ({event.severity.value.upper()})")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'table']),
              default='table', help='Output format')
def metrics(format):
    """Show analysis performance metrics"""
    try:
        config = get_analysis_config()
        orchestrator = AnalysisOrchestrator(config)
        
        metrics_data = {
            'orchestrator': orchestrator.get_orchestrator_metrics(),
            'entity_resolver': orchestrator.entity_resolver.get_resolution_metrics(),
            'enrichment_engine': orchestrator.enrichment_engine.get_enrichment_metrics(),
            'event_detector': orchestrator.event_detector.get_detection_metrics()
        }
        
        if format == 'json':
            click.echo(json.dumps(metrics_data, indent=2, default=str))
        else:
            for component, metrics in metrics_data.items():
                click.echo(f"\n{component.title()} Metrics:")
                for metric, value in metrics.items():
                    click.echo(f"  - {metric}: {value}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@analysis_cli.command()
def clear_cache():
    """Clear analysis caches"""
    try:
        config = get_analysis_config()
        orchestrator = AnalysisOrchestrator(config)
        
        orchestrator.enrichment_engine.clear_cache()
        click.echo("Analysis caches cleared successfully")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Utility functions

def load_entities_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load entities from JSON or CSV file"""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'entities' in data:
                return data['entities']
            else:
                raise ValueError("Invalid JSON format: expected list or object with 'entities' key")
    
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def output_results(result, output_file, format, verbose):
    """Output analysis results in specified format"""
    if format == 'json':
        output_data = result.__dict__
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
        else:
            click.echo(json.dumps(output_data, indent=2, default=str))
    
    elif format == 'table':
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Request ID', result.request_id],
            ['Analysis Date', result.analysis_date],
            ['Total Findings', result.summary.get('total_findings', 0)],
            ['Risk Level', result.summary.get('risk_assessment', 'UNKNOWN')],
            ['Duration (s)', result.metrics.get('duration_seconds', 0)]
        ]
        click.echo(tabulate(summary_data, headers='firstrow', tablefmt='grid'))
        
        if verbose:
            # Show detailed results
            if result.entity_resolutions:
                click.echo(f"\nEntity Resolutions ({len(result.entity_resolutions)}):")
                for resolution in result.entity_resolutions[:10]:  # Limit to 10
                    click.echo(f"  - Cluster {resolution['cluster_id']}: {len(resolution['entities'])} entities")
            
            if result.relationships:
                click.echo(f"\nRelationships ({len(result.relationships)}):")
                for rel in result.relationships[:10]:  # Limit to 10
                    click.echo(f"  - {rel['source_entity']} -> {rel['target_entity']} ({rel['relationship_type']})")
            
            if result.enrichments:
                click.echo(f"\nEnrichments ({len(result.enrichments)}):")
                for enrich in result.enrichments[:10]:  # Limit to 10
                    click.echo(f"  - {enrich['entity_id']}: {enrich['source_name']} ({enrich['enrichment_type']})")
            
            if result.events:
                click.echo(f"\nEvents ({len(result.events)}):")
                for event in result.events[:10]:  # Limit to 10
                    click.echo(f"  - {event['title']} ({event['severity'].upper()})")


def output_entity_clusters_table(clusters):
    """Output entity clusters in table format"""
    table_data = [['Cluster ID', 'Entity Count', 'Canonical Entity', 'Confidence']]
    
    for cluster_id, cluster_data in clusters.items():
        table_data.append([
            cluster_id,
            len(cluster_data['entities']),
            cluster_data['canonical_entity'].get('name', 'Unknown'),
            f"{cluster_data['confidence_score']:.3f}"
        ])
    
    click.echo(tabulate(table_data, headers='firstrow', tablefmt='grid'))


def output_relationships_table(relationships):
    """Output relationships in table format"""
    table_data = [['Source', 'Target', 'Type', 'Confidence']]
    
    for rel in relationships[:50]:  # Limit to 50 for readability
        table_data.append([
            rel.source_entity[:30],  # Truncate long names
            rel.target_entity[:30],
            rel.relationship_type,
            f"{rel.confidence_score:.3f}"
        ])
    
    click.echo(tabulate(table_data, headers='firstrow', tablefmt='grid'))


def output_enrichments_table(enrichments):
    """Output enrichments in table format"""
    table_data = [['Entity ID', 'Source', 'Type', 'Confidence', 'Cost']]
    
    for enrich in enrichments[:50]:  # Limit to 50 for readability
        table_data.append([
            enrich.entity_id[:20],  # Truncate long IDs
            enrich.source_name,
            enrich.enrichment_type,
            f"{enrich.confidence_score:.3f}",
            f"${enrich.cost:.2f}"
        ])
    
    click.echo(tabulate(table_data, headers='firstrow', tablefmt='grid'))


def output_events_table(events):
    """Output events in table format"""
    table_data = [['Title', 'Category', 'Severity', 'Confidence', 'Date']]
    
    for event in events[:50]:  # Limit to 50 for readability
        table_data.append([
            event.title[:40],  # Truncate long titles
            event.category.value,
            event.severity.value.upper(),
            f"{event.confidence_score:.3f}",
            event.event_date.strftime('%Y-%m-%d')
        ])
    
    click.echo(tabulate(table_data, headers='firstrow', tablefmt='grid'))


def output_entity_clusters_csv(clusters, output_file):
    """Output entity clusters to CSV"""
    data = []
    for cluster_id, cluster_data in clusters.items():
        data.append({
            'cluster_id': cluster_id,
            'entity_count': len(cluster_data['entities']),
            'canonical_name': cluster_data['canonical_entity'].get('name', ''),
            'confidence_score': cluster_data['confidence_score']
        })
    
    df = pd.DataFrame(data)
    if output_file:
        df.to_csv(output_file, index=False)
    else:
        click.echo(df.to_csv(index=False))


def output_relationships_csv(relationships, output_file):
    """Output relationships to CSV"""
    data = []
    for rel in relationships:
        data.append({
            'source_entity': rel.source_entity,
            'target_entity': rel.target_entity,
            'relationship_type': rel.relationship_type,
            'confidence_score': rel.confidence_score
        })
    
    df = pd.DataFrame(data)
    if output_file:
        df.to_csv(output_file, index=False)
    else:
        click.echo(df.to_csv(index=False))


def output_enrichments_csv(enrichments, output_file):
    """Output enrichments to CSV"""
    data = []
    for enrich in enrichments:
        data.append({
            'entity_id': enrich.entity_id,
            'source_name': enrich.source_name,
            'enrichment_type': enrich.enrichment_type,
            'confidence_score': enrich.confidence_score,
            'cost': enrich.cost
        })
    
    df = pd.DataFrame(data)
    if output_file:
        df.to_csv(output_file, index=False)
    else:
        click.echo(df.to_csv(index=False))


def output_events_csv(events, output_file):
    """Output events to CSV"""
    data = []
    for event in events:
        data.append({
            'event_id': event.event_id,
            'entity_id': event.entity_id,
            'title': event.title,
            'category': event.category.value,
            'severity': event.severity.value,
            'confidence_score': event.confidence_score,
            'event_date': event.event_date.isoformat()
        })
    
    df = pd.DataFrame(data)
    if output_file:
        df.to_csv(output_file, index=False)
    else:
        click.echo(df.to_csv(index=False))


if __name__ == '__main__':
    analysis_cli()
