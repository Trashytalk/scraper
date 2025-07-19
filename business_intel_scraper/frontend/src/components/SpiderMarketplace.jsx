import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Download, 
  Star, 
  Shield, 
  Package, 
  Filter,
  Grid,
  List,
  ExternalLink,
  Heart,
  Trash2,
  Eye,
  Code,
  Users,
  TrendingUp
} from 'lucide-react';

// Spider Marketplace Component
function SpiderMarketplace() {
  const [spiders, setSpiders] = useState([]);
  const [installedSpiders, setInstalledSpiders] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState('browse');

  const categories = [
    'business-intelligence',
    'news-scraping', 
    'social-media',
    'e-commerce',
    'job-boards',
    'research',
    'monitoring',
    'osint'
  ];

  useEffect(() => {
    loadMarketplaceData();
    loadStats();
  }, []);

  const loadMarketplaceData = async () => {
    setLoading(true);
    try {
      const [spidersResponse, installedResponse] = await Promise.all([
        fetch('/api/marketplace/search'),
        fetch('/api/marketplace/installed')
      ]);
      
      const spidersData = await spidersResponse.json();
      const installedData = await installedResponse.json();
      
      setSpiders(spidersData);
      setInstalledSpiders(installedData);
    } catch (error) {
      console.error('Failed to load marketplace data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/marketplace/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        category: selectedCategory,
        limit: '50'
      });
      
      const response = await fetch(`/api/marketplace/search?${params}`);
      const data = await response.json();
      setSpiders(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const installSpider = async (spiderName, version = 'latest') => {
    try {
      const response = await fetch('/api/marketplace/install', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: spiderName, version })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.message}`);
        loadMarketplaceData(); // Refresh data
      } else {
        alert(`❌ ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Installation failed: ${error.message}`);
    }
  };

  const uninstallSpider = async (spiderName) => {
    if (!confirm(`Are you sure you want to uninstall ${spiderName}?`)) return;
    
    try {
      const response = await fetch(`/api/marketplace/uninstall/${spiderName}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.message}`);
        loadMarketplaceData(); // Refresh data
      } else {
        alert(`❌ ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Uninstallation failed: ${error.message}`);
    }
  };

  const SpiderCard = ({ spider }) => (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Package className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
              <span>{spider.name}</span>
              {spider.verified && <Shield className="w-4 h-4 text-green-500" />}
            </h3>
            <p className="text-sm text-gray-600">v{spider.version} by {spider.author}</p>
          </div>
        </div>
        {spider.installed ? (
          <button
            onClick={() => uninstallSpider(spider.name)}
            className="flex items-center space-x-1 text-red-600 hover:text-red-700 text-sm"
          >
            <Trash2 className="w-4 h-4" />
            <span>Uninstall</span>
          </button>
        ) : (
          <button
            onClick={() => installSpider(spider.name, spider.version)}
            className="flex items-center space-x-1 bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 text-sm"
          >
            <Download className="w-4 h-4" />
            <span>Install</span>
          </button>
        )}
      </div>
      
      <p className="text-gray-700 text-sm mb-4 line-clamp-2">{spider.description}</p>
      
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <span className="bg-gray-100 px-2 py-1 rounded text-xs">{spider.category}</span>
        <div className="flex items-center space-x-4">
          {spider.rating > 0 && (
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span>{spider.rating.toFixed(1)}</span>
            </div>
          )}
          <div className="flex items-center space-x-1">
            <Download className="w-4 h-4" />
            <span>{spider.downloads?.toLocaleString() || 0}</span>
          </div>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-1 mb-4">
        {spider.tags?.slice(0, 3).map((tag, index) => (
          <span key={index} className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs">
            {tag}
          </span>
        ))}
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">{spider.license}</span>
        <div className="flex space-x-2">
          <button className="text-gray-400 hover:text-gray-600">
            <Eye className="w-4 h-4" />
          </button>
          <button className="text-gray-400 hover:text-gray-600">
            <Code className="w-4 h-4" />
          </button>
          <button className="text-gray-400 hover:text-gray-600">
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const SpiderListItem = ({ spider }) => (
    <div className="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Package className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-medium text-gray-900">{spider.name}</h3>
              {spider.verified && <Shield className="w-4 h-4 text-green-500" />}
            </div>
            <p className="text-sm text-gray-600">{spider.description}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="text-sm text-gray-500">
            <div>v{spider.version}</div>
            <div>{spider.author}</div>
          </div>
          
          <div className="text-sm text-gray-500 text-center">
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span>{spider.rating?.toFixed(1) || 'N/A'}</span>
            </div>
            <div>{spider.downloads?.toLocaleString() || 0} downloads</div>
          </div>
          
          {spider.installed ? (
            <button
              onClick={() => uninstallSpider(spider.name)}
              className="flex items-center space-x-1 text-red-600 hover:text-red-700 px-3 py-1 rounded"
            >
              <Trash2 className="w-4 h-4" />
              <span>Uninstall</span>
            </button>
          ) : (
            <button
              onClick={() => installSpider(spider.name, spider.version)}
              className="flex items-center space-x-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              <Download className="w-4 h-4" />
              <span>Install</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Spider Marketplace</h1>
        <div className="flex space-x-2">
          <button
            onClick={loadMarketplaceData}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Package className="w-8 h-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Spiders</p>
              <p className="text-xl font-bold text-gray-900">{stats.total_spiders || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Download className="w-8 h-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Installed</p>
              <p className="text-xl font-bold text-gray-900">{stats.installed_spiders || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Verified</p>
              <p className="text-xl font-bold text-gray-900">{stats.verified_spiders || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-orange-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Downloads</p>
              <p className="text-xl font-bold text-gray-900">{stats.total_downloads?.toLocaleString() || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search spiders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('browse')}
              className={`px-4 py-2 rounded-lg ${activeTab === 'browse' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Browse All
            </button>
            <button
              onClick={() => setActiveTab('installed')}
              className={`px-4 py-2 rounded-lg ${activeTab === 'installed' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Installed ({installedSpiders.length})
            </button>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Spider Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading spiders...</p>
          </div>
        </div>
      ) : (
        <div>
          {activeTab === 'browse' ? (
            viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {spiders.map((spider, index) => (
                  <SpiderCard key={index} spider={spider} />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {spiders.map((spider, index) => (
                  <SpiderListItem key={index} spider={spider} />
                ))}
              </div>
            )
          ) : (
            viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {installedSpiders.map((spider, index) => (
                  <SpiderCard key={index} spider={spider} />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {installedSpiders.map((spider, index) => (
                  <SpiderListItem key={index} spider={spider} />
                ))}
              </div>
            )
          )}
          
          {((activeTab === 'browse' && spiders.length === 0) || 
            (activeTab === 'installed' && installedSpiders.length === 0)) && (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {activeTab === 'browse' ? 'No spiders found' : 'No spiders installed'}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeTab === 'browse' 
                  ? 'Try adjusting your search criteria' 
                  : 'Browse the marketplace to install spiders'
                }
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SpiderMarketplace;
