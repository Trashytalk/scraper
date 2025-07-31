import React from 'react';

interface CrawlSummary {
  pages_processed: number;
  urls_discovered: number;
  total_crawl_time: number;
  average_page_time: number;
  duplicate_pages_skipped: number;
  errors_encountered: number;
  images_extracted: number;
  domains_crawled: string[];
}

interface CrawlStatusDisplayProps {
  summary: CrawlSummary;
  config: any;
  errors: any[];
  duplicateUrls: string[];
}

export const CrawlStatusDisplay: React.FC<CrawlStatusDisplayProps> = ({
  summary,
  config,
  errors,
  duplicateUrls
}) => {
  const successRate = summary.pages_processed / (summary.pages_processed + summary.errors_encountered) * 100;
  const pagesPerSecond = summary.pages_processed / summary.total_crawl_time;

  return (
    <div style={{
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      backgroundColor: '#f8f9fa',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 20px 0', color: '#1976d2' }}>
        📊 Crawl Status Summary
      </h3>

      {/* Performance Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '15px',
        marginBottom: '20px'
      }}>
        <div style={{
          padding: '15px',
          backgroundColor: '#d4edda',
          borderRadius: '6px',
          border: '1px solid #c3e6cb'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#155724' }}>
            {summary.pages_processed}
          </div>
          <div style={{ fontSize: '14px', color: '#155724' }}>Pages Processed</div>
        </div>

        <div style={{
          padding: '15px',
          backgroundColor: '#e3f2fd',
          borderRadius: '6px',
          border: '1px solid #bbdefb'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
            {summary.urls_discovered}
          </div>
          <div style={{ fontSize: '14px', color: '#1976d2' }}>URLs Discovered</div>
        </div>

        <div style={{
          padding: '15px',
          backgroundColor: '#fff3e0',
          borderRadius: '6px',
          border: '1px solid #ffe0b2'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f57c00' }}>
            {summary.total_crawl_time}s
          </div>
          <div style={{ fontSize: '14px', color: '#f57c00' }}>Total Time</div>
        </div>

        <div style={{
          padding: '15px',
          backgroundColor: '#f3e5f5',
          borderRadius: '6px',
          border: '1px solid #e1bee7'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
            {successRate.toFixed(1)}%
          </div>
          <div style={{ fontSize: '14px', color: '#7b1fa2' }}>Success Rate</div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '20px'
      }}>
        <div>
          <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>⚡ Performance</h4>
          <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <div>📈 <strong>Avg Page Time:</strong> {summary.average_page_time}s</div>
            <div>🚀 <strong>Pages/Second:</strong> {pagesPerSecond.toFixed(2)}</div>
            <div>🖼️ <strong>Images Extracted:</strong> {summary.images_extracted}</div>
            <div>🌐 <strong>Domains:</strong> {summary.domains_crawled.length}</div>
          </div>
        </div>

        <div>
          <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>🔍 Quality Metrics</h4>
          <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <div>✅ <strong>Successful:</strong> {summary.pages_processed}</div>
            <div>❌ <strong>Errors:</strong> {summary.errors_encountered}</div>
            <div>🔄 <strong>Duplicates:</strong> {summary.duplicate_pages_skipped}</div>
            <div>📊 <strong>Success Rate:</strong> {successRate.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Configuration Display */}
      <div style={{
        padding: '15px',
        backgroundColor: '#e9ecef',
        borderRadius: '6px',
        marginBottom: '15px'
      }}>
        <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>⚙️ Configuration Used</h5>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '10px',
          fontSize: '13px' 
        }}>
          <div>🎯 <strong>Max Depth:</strong> {config.max_depth}</div>
          <div>📄 <strong>Max Pages:</strong> {config.max_pages}</div>
          <div>📄 <strong>Full HTML:</strong> {config.extract_full_html ? '✅' : '❌'}</div>
          <div>🌐 <strong>Domain Crawl:</strong> {config.crawl_entire_domain ? '✅' : '❌'}</div>
          <div>🖼️ <strong>Enhanced Images:</strong> {config.include_images ? '✅' : '❌'}</div>
          <div>💾 <strong>Persistence:</strong> {config.save_to_database ? '✅' : '❌'}</div>
        </div>
      </div>

      {/* Domains Crawled */}
      {summary.domains_crawled.length > 0 && (
        <div style={{
          padding: '15px',
          backgroundColor: '#e8f5e8',
          borderRadius: '6px',
          marginBottom: '15px'
        }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#2e7d32' }}>🌐 Domains Crawled</h5>
          <div style={{ fontSize: '13px', color: '#2e7d32' }}>
            {summary.domains_crawled.join(' • ')}
          </div>
        </div>
      )}

      {/* Errors Section */}
      {errors.length > 0 && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          borderRadius: '6px',
          marginBottom: '15px'
        }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#721c24' }}>❌ Errors Encountered ({errors.length})</h5>
          <div style={{ maxHeight: '150px', overflow: 'auto', fontSize: '13px' }}>
            {errors.slice(0, 5).map((error, index) => (
              <div key={index} style={{ marginBottom: '8px', color: '#721c24' }}>
                <div><strong>URL:</strong> {error.url}</div>
                <div><strong>Error:</strong> {error.error}</div>
                <div><strong>Time:</strong> {new Date(error.timestamp).toLocaleTimeString()}</div>
                {index < errors.length - 1 && <hr style={{ margin: '8px 0', border: '1px solid #f5c6cb' }} />}
              </div>
            ))}
            {errors.length > 5 && (
              <div style={{ fontStyle: 'italic', color: '#6c757d' }}>
                ...and {errors.length - 5} more errors
              </div>
            )}
          </div>
        </div>
      )}

      {/* Duplicates Section */}
      {duplicateUrls.length > 0 && (
        <div style={{
          padding: '15px',
          backgroundColor: '#fff3cd',
          borderRadius: '6px'
        }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#856404' }}>🔄 Duplicate URLs Skipped ({duplicateUrls.length})</h5>
          <div style={{ maxHeight: '100px', overflow: 'auto', fontSize: '12px', color: '#856404' }}>
            {duplicateUrls.slice(0, 10).map((url, index) => (
              <div key={index}>{url}</div>
            ))}
            {duplicateUrls.length > 10 && (
              <div style={{ fontStyle: 'italic' }}>
                ...and {duplicateUrls.length - 10} more duplicates
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary Status */}
      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: summary.errors_encountered > 0 ? '#fff3cd' : '#d4edda',
        border: `1px solid ${summary.errors_encountered > 0 ? '#ffeaa7' : '#c3e6cb'}`,
        borderRadius: '6px',
        textAlign: 'center'
      }}>
        <div style={{ 
          fontSize: '16px', 
          fontWeight: 'bold',
          color: summary.errors_encountered > 0 ? '#856404' : '#155724'
        }}>
          {summary.errors_encountered === 0 
            ? '🎉 Crawl completed successfully!' 
            : `⚠️ Crawl completed with ${summary.errors_encountered} error${summary.errors_encountered > 1 ? 's' : ''}`
          }
        </div>
        <div style={{ 
          fontSize: '14px', 
          marginTop: '5px',
          color: summary.errors_encountered > 0 ? '#856404' : '#155724'
        }}>
          Processed {summary.pages_processed} pages in {summary.total_crawl_time}s
          {summary.images_extracted > 0 && ` • Extracted ${summary.images_extracted} images`}
        </div>
      </div>
    </div>
  );
};
