import React from 'react';

interface CrawlingConfig {
  max_depth: number;
  max_pages: number;
  follow_internal_links: boolean;
  follow_external_links: boolean;
  extract_full_html: boolean;
  crawl_entire_domain: boolean;
  include_images: boolean;
  save_to_database: boolean;
}

interface EnhancedCrawlingConfigProps {
  config: CrawlingConfig;
  onConfigChange: (config: CrawlingConfig) => void;
}

export const EnhancedCrawlingConfig: React.FC<EnhancedCrawlingConfigProps> = ({
  config,
  onConfigChange,
}) => {
  const updateConfig = (updates: Partial<CrawlingConfig>) => {
    onConfigChange({ ...config, ...updates });
  };

  return (
    <div style={{
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      marginBottom: '20px',
      backgroundColor: '#f8f9fa'
    }}>
      <h3 style={{ margin: '0 0 20px 0', color: '#1976d2' }}>
        🕷️ Enhanced Intelligent Crawling Configuration
      </h3>
      
      {/* Basic Crawling Settings */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '15px',
        marginBottom: '20px'
      }}>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>
            Max Depth:
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={config.max_depth}
            onChange={(e) => updateConfig({ max_depth: parseInt(e.target.value) })}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
          <small style={{ color: '#666' }}>How deep to crawl (1-10)</small>
        </div>
        
        <div>
          <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>
            Max Pages:
          </label>
          <input
            type="number"
            min="1"
            max="1000"
            value={config.max_pages}
            onChange={(e) => updateConfig({ max_pages: parseInt(e.target.value) })}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
          <small style={{ color: '#666' }}>Maximum pages to crawl</small>
        </div>
      </div>

      {/* Link Following Options */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>🔗 Link Following</h4>
        <div style={{ display: 'flex', gap: '20px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="checkbox"
              checked={config.follow_internal_links}
              onChange={(e) => updateConfig({ follow_internal_links: e.target.checked })}
            />
            <span>Follow Internal Links</span>
          </label>
          
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="checkbox"
              checked={config.follow_external_links}
              onChange={(e) => updateConfig({ follow_external_links: e.target.checked })}
            />
            <span>Follow External Links</span>
          </label>
        </div>
      </div>

      {/* Enhanced Extraction Options */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>📄 Enhanced Extraction</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <label style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: config.extract_full_html ? '#e3f2fd' : 'white'
          }}>
            <input
              type="checkbox"
              checked={config.extract_full_html}
              onChange={(e) => updateConfig({ extract_full_html: e.target.checked })}
            />
            <div>
              <div style={{ fontWeight: 'bold' }}>📄 Extract Full HTML</div>
              <small style={{ color: '#666' }}>Include complete HTML source</small>
            </div>
          </label>
          
          <label style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: config.crawl_entire_domain ? '#e8f5e8' : 'white'
          }}>
            <input
              type="checkbox"
              checked={config.crawl_entire_domain}
              onChange={(e) => updateConfig({ crawl_entire_domain: e.target.checked })}
            />
            <div>
              <div style={{ fontWeight: 'bold' }}>🌐 Crawl Entire Domain</div>
              <small style={{ color: '#666' }}>Include all subdomains</small>
            </div>
          </label>
          
          <label style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: config.include_images ? '#fff3e0' : 'white'
          }}>
            <input
              type="checkbox"
              checked={config.include_images}
              onChange={(e) => updateConfig({ include_images: e.target.checked })}
            />
            <div>
              <div style={{ fontWeight: 'bold' }}>🖼️ Enhanced Images</div>
              <small style={{ color: '#666' }}>Extract all images & metadata</small>
            </div>
          </label>
          
          <label style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: config.save_to_database ? '#f3e5f5' : 'white'
          }}>
            <input
              type="checkbox"
              checked={config.save_to_database}
              onChange={(e) => updateConfig({ save_to_database: e.target.checked })}
            />
            <div>
              <div style={{ fontWeight: 'bold' }}>💾 Data Persistence</div>
              <small style={{ color: '#666' }}>Save for caching & analysis</small>
            </div>
          </label>
        </div>
      </div>

      {/* Configuration Summary */}
      <div style={{
        padding: '15px',
        backgroundColor: '#e9ecef',
        borderRadius: '4px',
        border: '1px solid #ced4da'
      }}>
        <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>📋 Configuration Summary</h5>
        <div style={{ fontSize: '14px', color: '#6c757d', lineHeight: '1.4' }}>
          <div>🎯 Will crawl up to <strong>{config.max_pages}</strong> pages at depth <strong>{config.max_depth}</strong></div>
          <div>🔗 Links: {config.follow_internal_links ? '✅ Internal' : '❌ Internal'} | {config.follow_external_links ? '✅ External' : '❌ External'}</div>
          <div>📄 HTML: {config.extract_full_html ? '✅ Full HTML' : '📝 Text only'} | 🌐 Domain: {config.crawl_entire_domain ? '✅ Entire domain' : '🎯 Single domain'}</div>
          <div>🖼️ Images: {config.include_images ? '✅ Enhanced extraction' : '📷 Basic only'} | 💾 Storage: {config.save_to_database ? '✅ Persistent' : '⚡ Memory only'}</div>
        </div>
      </div>

      {/* Estimated Performance */}
      <div style={{
        marginTop: '15px',
        padding: '10px',
        backgroundColor: '#fff3cd',
        border: '1px solid #ffeaa7',
        borderRadius: '4px'
      }}>
        <div style={{ fontSize: '12px', color: '#856404' }}>
          <strong>⚡ Estimated Performance:</strong> 
          {' '}~{Math.ceil(config.max_pages * (config.extract_full_html ? 2 : 1) * (config.include_images ? 1.5 : 1))}s crawl time
          {config.crawl_entire_domain && ' (domain crawling may take longer)'}
        </div>
      </div>
    </div>
  );
};
