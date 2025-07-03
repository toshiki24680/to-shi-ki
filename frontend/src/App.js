import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// 数据面板组件
const DataPanel = ({ data, stats, autoCrawlStatus, onToggleAutoCrawl, version }) => {
  return (
    <div className="space-y-6">
      {/* 版本信息和自动爬虫控制 */}
      <div style={{ background: 'rgba(76, 175, 80, 0.1)', border: '2px solid #4CAF50', padding: '20px', borderRadius: '15px' }}>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#2E7D32', fontSize: '18px' }}>🎯 v2.5 自动化增强版</h4>
            <div style={{ color: '#2E7D32', fontSize: '14px' }}>
              <strong>45秒自动爬虫 • 多账号管理 • 数据累计 • 关键词统计</strong>
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => onToggleAutoCrawl(!autoCrawlStatus.running)}
              style={{
                padding: '12px 24px',
                background: autoCrawlStatus.running ? 'linear-gradient(45deg, #ff4757, #ff3838)' : 'linear-gradient(45deg, #2ed573, #1dd1a1)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
              }}
            >
              {autoCrawlStatus.running ? '🛑 停止自动爬虫' : '🚀 启动自动爬虫'}
            </button>
          </div>
        </div>
        
        {autoCrawlStatus.running && (
          <div style={{ padding: '12px', background: 'rgba(46, 213, 115, 0.1)', borderRadius: '8px', border: '1px solid #2ed573' }}>
            <p style={{ margin: '0', color: '#2E7D32', fontSize: '14px' }}>
              🔄 自动爬虫运行中 | 间隔: 45秒 | 活跃账号: {autoCrawlStatus.active_accounts}/{autoCrawlStatus.total_accounts}
            </p>
          </div>
        )}
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)', padding: '20px', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>{stats.total_accounts}</div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>总账号数</div>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #f093fb, #f5576c)', padding: '20px', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>{stats.total_records}</div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>总记录数</div>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #4facfe, #00f2fe)', padding: '20px', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>{stats.active_accounts}</div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>活跃账号</div>
          </div>
          <div style={{ background: 'linear-gradient(135deg, #43e97b, #38f9d7)', padding: '20px', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>{stats.keyword_alerts || 0}</div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>关键词提醒</div>
          </div>
        </div>
      )}

      {/* 数据表格 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>🗂️ 实时师门数据</h3>
        {data.length > 0 ? (
          <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead style={{ background: '#f8f9fa', position: 'sticky', top: 0 }}>
                <tr>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>账号</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>角色</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>类型</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>等级</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>门派</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>进度</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>累计</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>状态</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>时间</th>
                </tr>
              </thead>
              <tbody>
                {data.slice(0, 50).map((item, i) => (
                  <tr key={i} style={{ ':hover': { background: '#f8f9fa' } }}>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6', fontWeight: '500' }}>{item.account_username}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.name}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '12px', 
                        background: item.type === '跑商' ? '#e3f2fd' : '#f3e5f5',
                        color: item.type === '跑商' ? '#1976d2' : '#7b1fa2',
                        fontSize: '12px'
                      }}>
                        {item.type}
                      </span>
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.level}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.guild}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                      <div style={{ color: '#667eea', fontWeight: 'bold' }}>
                        {item.count_current}/{item.count_total}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        周期: {item.cycle_count || 0}
                      </div>
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                      <div style={{ color: '#f093fb', fontWeight: 'bold' }}>
                        {item.accumulated_count || 0}
                      </div>
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '12px', 
                        background: item.status.includes('在线') ? '#d4edda' : item.status.includes('没钱') ? '#f8d7da' : '#fff3cd',
                        color: item.status.includes('在线') ? '#155724' : item.status.includes('没钱') ? '#721c24' : '#856404',
                        fontSize: '12px'
                      }}>
                        {item.status.length > 15 ? item.status.substring(0, 15) + '...' : item.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6', fontSize: '12px', color: '#666' }}>
                      {new Date(item.crawl_timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>暂无师门数据，启动自动爬虫开始监控</p>
          </div>
        )}
      </div>
    </div>
  );
};

// 数据筛选组件
const DataFilter = ({ data, onExport }) => {
  const [filters, setFilters] = useState({
    account_username: '',
    guild: '',
    type: '',
    status: '',
    min_level: '',
    max_level: '',
    keyword: ''
  });
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFilter = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/crawler/data/filter`, filters);
      setFilteredData(response.data.data);
    } catch (error) {
      console.error('筛选失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetFilters = () => {
    setFilters({
      account_username: '',
      guild: '',
      type: '',
      status: '',
      min_level: '',
      max_level: '',
      keyword: ''
    });
    setFilteredData([]);
  };

  useEffect(() => {
    setFilteredData(data);
  }, [data]);

  return (
    <div className="space-y-6">
      {/* 筛选条件 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>🔍 数据筛选器</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>账号</label>
            <input
              type="text"
              value={filters.account_username}
              onChange={(e) => setFilters({...filters, account_username: e.target.value})}
              placeholder="输入账号名"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none',
                transition: 'border-color 0.3s'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>门派</label>
            <input
              type="text"
              value={filters.guild}
              onChange={(e) => setFilters({...filters, guild: e.target.value})}
              placeholder="输入门派名"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>类型</label>
            <input
              type="text"
              value={filters.type}
              onChange={(e) => setFilters({...filters, type: e.target.value})}
              placeholder="输入类型"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>最低等级</label>
            <input
              type="number"
              value={filters.min_level}
              onChange={(e) => setFilters({...filters, min_level: e.target.value})}
              placeholder="如: 80"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>最高等级</label>
            <input
              type="number"
              value={filters.max_level}
              onChange={(e) => setFilters({...filters, max_level: e.target.value})}
              placeholder="如: 120"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500', color: '#555' }}>关键词</label>
            <input
              type="text"
              value={filters.keyword}
              onChange={(e) => setFilters({...filters, keyword: e.target.value})}
              placeholder="搜索角色名或状态"
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '8px',
                outline: 'none'
              }}
            />
          </div>
        </div>
        
        <div className="flex gap-3">
          <button 
            onClick={handleFilter}
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(45deg, #667eea, #764ba2)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? '筛选中...' : '🔍 应用筛选'}
          </button>
          
          <button 
            onClick={resetFilters}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(45deg, #ff7675, #fd79a8)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600'
            }}
          >
            🔄 重置筛选
          </button>
          
          <button 
            onClick={onExport}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(45deg, #00b894, #00cec9)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600'
            }}
          >
            📁 导出数据
          </button>
        </div>
      </div>

      {/* 筛选结果 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <div className="flex justify-between items-center mb-4">
          <h3 style={{ margin: '0', color: '#333', fontSize: '20px' }}>📊 筛选结果</h3>
          <div style={{ color: '#666', fontSize: '14px' }}>
            显示 {filteredData.length} / {data.length} 条记录
          </div>
        </div>
        
        {filteredData.length > 0 ? (
          <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead style={{ background: '#f8f9fa', position: 'sticky', top: 0 }}>
                <tr>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>账号</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>角色</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>等级</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>门派</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>进度</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>状态</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((item, i) => (
                  <tr key={i}>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6', fontWeight: '500' }}>{item.account_username}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.name}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.level}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{item.guild}</td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6', color: '#667eea', fontWeight: 'bold' }}>
                      {item.count_current}/{item.count_total}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                      {item.status.length > 20 ? item.status.substring(0, 20) + '...' : item.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>无匹配数据，请调整筛选条件</p>
          </div>
        )}
      </div>
    </div>
  );
};

// 账号管理组件
const AccountManagement = ({ accounts, onRefresh }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAccount, setNewAccount] = useState({ username: '', password: '', preferred_guild: '' });
  const [selectedAccounts, setSelectedAccounts] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAddAccount = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/accounts`, newAccount);
      setNewAccount({ username: '', password: '', preferred_guild: '' });
      setShowAddForm(false);
      onRefresh();
      alert('账号添加成功！');
    } catch (error) {
      alert('添加失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (!window.confirm('确定要删除这个账号吗？')) return;
    
    try {
      await axios.delete(`${API}/accounts/${accountId}`);
      onRefresh();
      alert('账号删除成功！');
    } catch (error) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleBatchOperation = async (operation) => {
    if (selectedAccounts.length === 0) {
      alert('请先选择要操作的账号');
      return;
    }

    try {
      await axios.post(`${API}/accounts/batch`, {
        account_ids: selectedAccounts,
        operation: operation
      });
      setSelectedAccounts([]);
      onRefresh();
      alert(`批量${operation}操作成功！`);
    } catch (error) {
      alert('批量操作失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const toggleAccountSelection = (accountId) => {
    setSelectedAccounts(prev => 
      prev.includes(accountId) 
        ? prev.filter(id => id !== accountId)
        : [...prev, accountId]
    );
  };

  return (
    <div className="space-y-6">
      {/* 添加账号表单 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <div className="flex justify-between items-center mb-4">
          <h3 style={{ margin: '0', color: '#333', fontSize: '20px' }}>👥 账号管理</h3>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(45deg, #667eea, #764ba2)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600'
            }}
          >
            {showAddForm ? '取消添加' : '➕ 添加账号'}
          </button>
        </div>

        {showAddForm && (
          <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>用户名</label>
                <input
                  type="text"
                  value={newAccount.username}
                  onChange={(e) => setNewAccount({...newAccount, username: e.target.value})}
                  placeholder="输入用户名"
                  style={{ width: '100%', padding: '10px', border: '2px solid #e1e5e9', borderRadius: '8px' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>密码</label>
                <input
                  type="password"
                  value={newAccount.password}
                  onChange={(e) => setNewAccount({...newAccount, password: e.target.value})}
                  placeholder="输入密码"
                  style={{ width: '100%', padding: '10px', border: '2px solid #e1e5e9', borderRadius: '8px' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>首选门派</label>
                <input
                  type="text"
                  value={newAccount.preferred_guild}
                  onChange={(e) => setNewAccount({...newAccount, preferred_guild: e.target.value})}
                  placeholder="可选"
                  style={{ width: '100%', padding: '10px', border: '2px solid #e1e5e9', borderRadius: '8px' }}
                />
              </div>
            </div>
            <button 
              onClick={handleAddAccount}
              disabled={loading || !newAccount.username || !newAccount.password}
              style={{
                padding: '10px 20px',
                background: 'linear-gradient(45deg, #00b894, #00cec9)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '添加中...' : '✅ 确认添加'}
            </button>
          </div>
        )}

        {/* 批量操作 */}
        {selectedAccounts.length > 0 && (
          <div style={{ background: '#e3f2fd', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
            <div className="flex gap-3 items-center">
              <span style={{ color: '#1976d2', fontWeight: '500' }}>
                已选择 {selectedAccounts.length} 个账号:
              </span>
              <button onClick={() => handleBatchOperation('start')} style={{ padding: '6px 12px', background: '#4caf50', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px' }}>批量启动</button>
              <button onClick={() => handleBatchOperation('stop')} style={{ padding: '6px 12px', background: '#ff9800', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px' }}>批量停止</button>
              <button onClick={() => handleBatchOperation('delete')} style={{ padding: '6px 12px', background: '#f44336', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px' }}>批量删除</button>
              <button onClick={() => setSelectedAccounts([])} style={{ padding: '6px 12px', background: '#757575', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px' }}>取消选择</button>
            </div>
          </div>
        )}
      </div>

      {/* 账号列表 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>🗂️ 账号列表</h3>
        
        {accounts.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {accounts.map((acc) => (
              <div key={acc.id} style={{ 
                background: selectedAccounts.includes(acc.id) ? '#e3f2fd' : 'linear-gradient(135deg, #fff, #f8f9fa)', 
                padding: '20px', 
                borderRadius: '12px', 
                border: selectedAccounts.includes(acc.id) ? '2px solid #2196f3' : '2px solid #e9ecef',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                cursor: 'pointer'
              }}
              onClick={() => toggleAccountSelection(acc.id)}>
                
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 style={{ margin: '0', color: '#333', fontSize: '16px' }}>{acc.username}</h4>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                      ID: {acc.id.substring(0, 8)}...
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '12px', 
                      background: acc.status === 'active' ? '#d4edda' : acc.status === 'error' ? '#f8d7da' : '#fff3cd',
                      color: acc.status === 'active' ? '#155724' : acc.status === 'error' ? '#721c24' : '#856404',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {acc.status === 'active' ? '🟢 活跃' : acc.status === 'error' ? '🔴 错误' : '🟡 待机'}
                    </span>
                  </div>
                </div>

                <div style={{ fontSize: '13px', color: '#666', marginBottom: '15px' }}>
                  <div>爬取次数: {acc.crawl_count || 0}</div>
                  <div>成功率: {((acc.success_rate || 0) * 100).toFixed(1)}%</div>
                  <div>自动启用: {acc.is_auto_enabled ? '是' : '否'}</div>
                  {acc.last_crawl && (
                    <div>最后爬取: {new Date(acc.last_crawl).toLocaleString()}</div>
                  )}
                  {acc.last_error && (
                    <div style={{ color: '#dc3545', marginTop: '5px' }}>
                      错误: {acc.last_error.substring(0, 50)}...
                    </div>
                  )}
                </div>

                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <button 
                    onClick={() => handleDeleteAccount(acc.id)}
                    style={{
                      flex: 1,
                      padding: '8px',
                      background: 'linear-gradient(45deg, #ff4757, #ff3838)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}
                  >
                    🗑️ 删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>暂无账号，点击"添加账号"开始</p>
          </div>
        )}
      </div>
    </div>
  );
};

// 统计分析组件
const StatisticsAnalysis = ({ statistics, crawlHistory }) => {
  if (!statistics) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
        <p>加载统计数据中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 基础统计 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>📊 基础统计</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
          <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>{statistics.basic_stats?.total_records || 0}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>总记录数</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f093fb' }}>{statistics.basic_stats?.unique_accounts || 0}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>独立账号</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4facfe' }}>{statistics.basic_stats?.unique_guilds || 0}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>不同门派</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#43e97b' }}>{statistics.basic_stats?.avg_level || 0}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>平均等级</div>
          </div>
        </div>
      </div>

      {/* 累计数据统计 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>🔄 累计数据统计</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #667eea, #764ba2)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {statistics.accumulation_stats?.total_accumulated_count || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>总累计次数</div>
          </div>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #f093fb, #f5576c)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {statistics.accumulation_stats?.total_cycles || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>总重置周期</div>
          </div>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #4facfe, #00f2fe)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {statistics.accumulation_stats?.avg_accumulated_per_record || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>平均累计/记录</div>
          </div>
        </div>
      </div>

      {/* 分布统计 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* 账号分布 */}
        <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '16px' }}>👤 账号数据分布</h4>
          {statistics.account_distribution && Object.keys(statistics.account_distribution).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(statistics.account_distribution).map(([account, count]) => (
                <div key={account} className="flex justify-between items-center">
                  <span style={{ fontSize: '14px' }}>{account}</span>
                  <span style={{ 
                    padding: '2px 8px', 
                    background: '#667eea', 
                    color: 'white', 
                    borderRadius: '12px', 
                    fontSize: '12px' 
                  }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#666', fontSize: '14px' }}>暂无数据</div>
          )}
        </div>

        {/* 门派分布 */}
        <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '16px' }}>🏠 门派分布</h4>
          {statistics.guild_distribution && Object.keys(statistics.guild_distribution).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(statistics.guild_distribution).slice(0, 8).map(([guild, count]) => (
                <div key={guild} className="flex justify-between items-center">
                  <span style={{ fontSize: '14px' }}>{guild || '无门派'}</span>
                  <span style={{ 
                    padding: '2px 8px', 
                    background: '#f093fb', 
                    color: 'white', 
                    borderRadius: '12px', 
                    fontSize: '12px' 
                  }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#666', fontSize: '14px' }}>暂无数据</div>
          )}
        </div>

        {/* 类型分布 */}
        <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '16px' }}>⚔️ 类型分布</h4>
          {statistics.type_distribution && Object.keys(statistics.type_distribution).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(statistics.type_distribution).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span style={{ fontSize: '14px' }}>{type || '未知'}</span>
                  <span style={{ 
                    padding: '2px 8px', 
                    background: '#4facfe', 
                    color: 'white', 
                    borderRadius: '12px', 
                    fontSize: '12px' 
                  }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#666', fontSize: '14px' }}>暂无数据</div>
          )}
        </div>
      </div>

      {/* 爬取历史 */}
      {crawlHistory && (
        <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>📈 爬取历史</h3>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
              <div style={{ textAlign: 'center', padding: '15px', background: '#e8f5e8', borderRadius: '10px' }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#4caf50' }}>{crawlHistory.total_crawls}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>总爬取次数</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', background: '#e3f2fd', borderRadius: '10px' }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#2196f3' }}>
                  {(crawlHistory.success_rate * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>成功率</div>
              </div>
            </div>
          </div>

          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {crawlHistory.history && crawlHistory.history.length > 0 ? (
              <div className="space-y-2">
                {crawlHistory.history.slice(-20).reverse().map((entry, i) => (
                  <div key={i} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: entry.success ? '#f1f8e9' : '#ffebee',
                    borderRadius: '8px',
                    fontSize: '13px'
                  }}>
                    <span>{entry.account}</span>
                    <span>{entry.success ? '✅' : '❌'} {entry.data_count} 条</span>
                    <span style={{ color: '#666' }}>
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#666' }}>暂无爬取历史</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// 关键词统计组件
const KeywordStatistics = ({ keywordStats, onResetKeywords }) => {
  const [alertThreshold, setAlertThreshold] = useState(5);

  if (!keywordStats) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
        <p>加载关键词统计中...</p>
      </div>
    );
  }

  const highAlertKeywords = Object.entries(keywordStats.keyword_stats || {})
    .filter(([_, count]) => count >= alertThreshold);

  return (
    <div className="space-y-6">
      {/* 关键词监控概览 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <div className="flex justify-between items-center mb-4">
          <h3 style={{ margin: '0', color: '#333', fontSize: '20px' }}>🚨 关键词监控</h3>
          <button 
            onClick={onResetKeywords}
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(45deg, #ff7675, #fd79a8)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600'
            }}
          >
            🔄 重置统计
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #ff6b6b, #ee5a24)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {keywordStats.total_keywords_detected || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>总检测次数</div>
          </div>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #feca57, #ff9ff3)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {keywordStats.unique_keywords || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>触发关键词数</div>
          </div>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #48dbfb, #0abde3)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {keywordStats.monitored_keywords?.length || 0}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>监控关键词数</div>
          </div>
          <div style={{ padding: '20px', background: 'linear-gradient(135deg, #ff9ff3, #f368e0)', borderRadius: '12px', color: 'white' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
              {highAlertKeywords.length}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.9' }}>高频预警</div>
          </div>
        </div>

        {/* 预警阈值设置 */}
        <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
          <div className="flex items-center gap-3">
            <label style={{ fontWeight: '500', color: '#555' }}>预警阈值:</label>
            <input
              type="number"
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(Number(e.target.value))}
              min="1"
              style={{ 
                width: '80px', 
                padding: '6px', 
                border: '2px solid #e1e5e9', 
                borderRadius: '6px' 
              }}
            />
            <span style={{ color: '#666', fontSize: '14px' }}>次以上显示为高频预警</span>
          </div>
        </div>

        {/* 高频预警 */}
        {highAlertKeywords.length > 0 && (
          <div style={{ background: '#ffebee', border: '2px solid #f44336', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#d32f2f', fontSize: '16px' }}>⚠️ 高频预警关键词</h4>
            <div className="space-y-2">
              {highAlertKeywords.map(([keyword, count]) => (
                <div key={keyword} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 12px',
                  background: 'white',
                  borderRadius: '8px',
                  border: '1px solid #f44336'
                }}>
                  <span style={{ fontWeight: '500', color: '#d32f2f' }}>{keyword}</span>
                  <span style={{ 
                    padding: '4px 8px', 
                    background: '#f44336', 
                    color: 'white', 
                    borderRadius: '12px', 
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}>
                    {count} 次
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 监控关键词列表 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>🔍 监控关键词列表</h3>
        
        {keywordStats.monitored_keywords && keywordStats.monitored_keywords.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '10px' }}>
            {keywordStats.monitored_keywords.map((keyword, i) => {
              const count = keywordStats.keyword_stats[keyword] || 0;
              return (
                <div key={i} style={{ 
                  padding: '12px', 
                  background: count > 0 ? '#ffebee' : '#f8f9fa',
                  borderRadius: '8px',
                  border: count > 0 ? '2px solid #f44336' : '1px solid #e9ecef',
                  textAlign: 'center'
                }}>
                  <div style={{ fontWeight: '500', color: count > 0 ? '#d32f2f' : '#555', marginBottom: '4px' }}>
                    {keyword}
                  </div>
                  <div style={{ 
                    fontSize: '12px', 
                    color: count > 0 ? '#d32f2f' : '#666',
                    fontWeight: count > 0 ? 'bold' : 'normal'
                  }}>
                    {count} 次
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#666' }}>暂无监控关键词</div>
        )}
      </div>

      {/* 关键词统计详情 */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '25px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#333', fontSize: '20px' }}>📊 关键词统计详情</h3>
        
        {keywordStats.keyword_stats && Object.keys(keywordStats.keyword_stats).length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead style={{ background: '#f8f9fa' }}>
                <tr>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>关键词</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>检测次数</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>风险级别</th>
                  <th style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '600' }}>处理建议</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(keywordStats.keyword_stats)
                  .sort(([,a], [,b]) => b - a)
                  .map(([keyword, count]) => {
                    const riskLevel = count >= 10 ? '高' : count >= 5 ? '中' : '低';
                    const riskColor = count >= 10 ? '#f44336' : count >= 5 ? '#ff9800' : '#4caf50';
                    
                    return (
                      <tr key={keyword}>
                        <td style={{ padding: '10px', border: '1px solid #dee2e6', fontWeight: '500' }}>
                          {keyword}
                        </td>
                        <td style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'center' }}>
                          <span style={{ 
                            padding: '4px 8px', 
                            background: riskColor, 
                            color: 'white', 
                            borderRadius: '12px', 
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            {count}
                          </span>
                        </td>
                        <td style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'center' }}>
                          <span style={{ color: riskColor, fontWeight: '500' }}>{riskLevel}</span>
                        </td>
                        <td style={{ padding: '10px', border: '1px solid #dee2e6', fontSize: '12px', color: '#666' }}>
                          {count >= 10 ? '立即检查账号状态' : 
                           count >= 5 ? '关注账号运行情况' : '正常监控'}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>暂无关键词统计数据</p>
          </div>
        )}
      </div>
    </div>
  );
};

// 主应用组件
function App() {
  const [activeTab, setActiveTab] = useState('data');
  const [data, setData] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [stats, setStats] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [keywordStats, setKeywordStats] = useState(null);
  const [crawlHistory, setCrawlHistory] = useState(null);
  const [autoCrawlStatus, setAutoCrawlStatus] = useState({ running: false });
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(false);

  // 获取数据
  const fetchData = async () => {
    try {
      const [dataRes, accountsRes, statsRes, versionRes] = await Promise.all([
        axios.get(`${API}/crawler/data`),
        axios.get(`${API}/accounts`),
        axios.get(`${API}/crawler/status`),
        axios.get(`${API}/version`)
      ]);
      setData(dataRes.data);
      setAccounts(accountsRes.data);
      setStats(statsRes.data);
      setVersion(versionRes.data);
    } catch (err) {
      console.error('获取数据失败:', err);
    }
  };

  // 获取统计数据
  const fetchStatistics = async () => {
    try {
      const [statisticsRes, keywordRes, historyRes] = await Promise.all([
        axios.get(`${API}/crawler/stats`),
        axios.get(`${API}/crawler/keywords`),
        axios.get(`${API}/crawler/history`)
      ]);
      setStatistics(statisticsRes.data);
      setKeywordStats(keywordRes.data);
      setCrawlHistory(historyRes.data);
    } catch (err) {
      console.error('获取统计数据失败:', err);
    }
  };

  // 获取自动爬虫状态
  const fetchAutoCrawlStatus = async () => {
    try {
      const response = await axios.get(`${API}/crawler/auto/status`);
      setAutoCrawlStatus(response.data);
    } catch (err) {
      console.error('获取自动爬虫状态失败:', err);
    }
  };

  // 切换自动爬虫
  const handleToggleAutoCrawl = async (start) => {
    setLoading(true);
    try {
      if (start) {
        await axios.post(`${API}/crawler/auto/start`);
        alert('自动爬虫启动成功！');
      } else {
        await axios.post(`${API}/crawler/auto/stop`);
        alert('自动爬虫停止成功！');
      }
      fetchAutoCrawlStatus();
    } catch (err) {
      alert('操作失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // 导出CSV
  const handleExport = async () => {
    try {
      const response = await axios.get(`${API}/crawler/data/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'guild_crawler_v2.5_enhanced.csv';
      link.click();
      alert('数据导出成功！');
    } catch (err) {
      alert('导出失败');
    }
  };

  // 重置关键词统计
  const handleResetKeywords = async () => {
    if (!window.confirm('确定要重置关键词统计吗？')) return;
    
    try {
      await axios.post(`${API}/crawler/keywords/reset`);
      fetchStatistics();
      alert('关键词统计已重置！');
    } catch (err) {
      alert('重置失败');
    }
  };

  // 初始化和定时刷新
  useEffect(() => {
    fetchData();
    fetchStatistics();
    fetchAutoCrawlStatus();

    // 每30秒刷新数据
    const interval = setInterval(() => {
      fetchData();
      fetchAutoCrawlStatus();
      if (activeTab === 'statistics') {
        fetchStatistics();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // 标签切换时刷新对应数据
  useEffect(() => {
    if (activeTab === 'statistics') {
      fetchStatistics();
    }
  }, [activeTab]);

  const tabs = [
    { id: 'data', name: '🏠 数据面板', component: DataPanel },
    { id: 'filter', name: '🔍 数据筛选', component: DataFilter },
    { id: 'accounts', name: '👥 账号管理', component: AccountManagement },
    { id: 'statistics', name: '📊 统计分析', component: StatisticsAnalysis },
    { id: 'keywords', name: '🚨 关键词统计', component: KeywordStatistics }
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* 头部 */}
      <div style={{ background: 'rgba(255,255,255,0.95)', padding: '20px 30px', boxShadow: '0 2px 20px rgba(0,0,0,0.1)' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h1 style={{ 
                margin: '0', 
                background: 'linear-gradient(45deg, #667eea, #764ba2)', 
                WebkitBackgroundClip: 'text', 
                WebkitTextFillColor: 'transparent', 
                fontSize: '32px',
                fontWeight: '700'
              }}>
                🚀 小八爬虫管理系统
              </h1>
              {version && (
                <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '16px' }}>
                  师门登录优化版 v{version.version} | 自动化增强版 | {stats?.system_info}
                </p>
              )}
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ 
                padding: '10px 20px', 
                background: autoCrawlStatus.running ? 'linear-gradient(45deg, #00b894, #00cec9)' : 'linear-gradient(45deg, #ddd, #ccc)',
                borderRadius: '25px',
                color: autoCrawlStatus.running ? 'white' : '#666',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {autoCrawlStatus.running ? '🟢 自动爬虫运行中' : '🔴 自动爬虫已停止'}
              </div>
            </div>
          </div>
          
          {/* 标签导航 */}
          <div style={{ display: 'flex', gap: '5px', borderBottom: '2px solid #f1f3f4' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '12px 24px',
                  border: 'none',
                  background: activeTab === tab.id ? 'linear-gradient(45deg, #667eea, #764ba2)' : 'transparent',
                  color: activeTab === tab.id ? 'white' : '#666',
                  borderRadius: '10px 10px 0 0',
                  fontWeight: activeTab === tab.id ? '600' : '500',
                  fontSize: '16px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '30px' }}>
        {ActiveComponent && (
          <ActiveComponent
            data={data}
            accounts={accounts}
            stats={stats}
            statistics={statistics}
            keywordStats={keywordStats}
            crawlHistory={crawlHistory}
            autoCrawlStatus={autoCrawlStatus}
            version={version}
            onRefresh={fetchData}
            onToggleAutoCrawl={handleToggleAutoCrawl}
            onExport={handleExport}
            onResetKeywords={handleResetKeywords}
          />
        )}
      </div>
    </div>
  );
}

export default App;