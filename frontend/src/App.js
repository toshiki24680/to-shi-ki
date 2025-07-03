import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [dataRes, statsRes, accountsRes, versionRes] = await Promise.all([
        axios.get(`${API}/crawler/data`),
        axios.get(`${API}/crawler/status`),
        axios.get(`${API}/crawler/accounts`),
        axios.get(`${API}/version`)
      ]);
      setData(dataRes.data);
      setStats(statsRes.data);
      setAccounts(accountsRes.data);
      setVersion(versionRes.data);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const startCrawler = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/crawler/start`);
      await fetchData();
      alert('师门爬虫启动成功！');
    } finally {
      setLoading(false);
    }
  };

  const generateData = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/crawler/mock-data`);
      await fetchData();
      alert('师门演示数据生成成功！');
    } finally {
      setLoading(false);
    }
  };

  const testOptimizedLogin = async (username) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/crawler/test/${username}`);
      alert(`师门登录优化版测试结果:\n\n用户: ${response.data.username}\n结果: ${response.data.test_result}\n版本: ${response.data.version}\n详情: ${response.data.message}`);
      await fetchData();
    } catch (err) {
      alert('测试失败: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = async () => {
    try {
      const response = await axios.get(`${API}/crawler/data/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'guild_crawler_v2.1.csv';
      link.click();
    } catch (err) {
      alert('导出失败');
    }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', background: 'linear-gradient(135deg, #667eea, #764ba2)', minHeight: '100vh' }}>
      {/* 头部 */}
      <div style={{ background: 'rgba(255,255,255,0.95)', padding: '25px', borderRadius: '15px', marginBottom: '20px', boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <h1 style={{ margin: '0', background: 'linear-gradient(45deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '28px' }}>
              🚀 小八爬虫管理系统
            </h1>
            {version && (
              <div style={{ margin: '5px 0 0 0', color: '#666' }}>
                <p style={{ margin: '0', fontWeight: '500' }}>
                  师门登录优化版 v{version.version} | 更新: {version.update_date} | {stats?.system_info}
                </p>
                <div style={{ background: 'linear-gradient(45deg, #4CAF50, #45a049)', color: 'white', padding: '8px 12px', borderRadius: '20px', display: 'inline-block', marginTop: '8px', fontSize: '14px' }}>
                  ✨ 最新优化：精确师门登录 + 多策略按钮识别
                </div>
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button onClick={startCrawler} disabled={loading} style={{
              padding: '14px 28px', background: 'linear-gradient(45deg, #667eea, #764ba2)', 
              color: 'white', border: 'none', borderRadius: '10px', fontWeight: '600', fontSize: '16px',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
            }}>
              {loading ? '处理中...' : '启动师门爬虫'}
            </button>
            <button onClick={generateData} disabled={loading} style={{
              padding: '14px 28px', background: 'linear-gradient(45deg, #f093fb, #f5576c)', 
              color: 'white', border: 'none', borderRadius: '10px', fontWeight: '600', fontSize: '16px',
              boxShadow: '0 4px 15px rgba(240, 147, 251, 0.4)'
            }}>
              生成演示数据
            </button>
            <button onClick={exportCsv} style={{
              padding: '14px 28px', background: 'linear-gradient(45deg, #4facfe, #00f2fe)', 
              color: 'white', border: 'none', borderRadius: '10px', fontWeight: '600', fontSize: '16px',
              boxShadow: '0 4px 15px rgba(79, 172, 254, 0.4)'
            }}>
              导出CSV
            </button>
          </div>
        </div>
      </div>

      {/* 优化说明 */}
      <div style={{ background: 'rgba(76, 175, 80, 0.1)', border: '2px solid #4CAF50', padding: '20px', borderRadius: '15px', marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#2E7D32', fontSize: '18px' }}>🎯 v2.1 师门登录优化亮点</h4>
        <div style={{ color: '#2E7D32', lineHeight: '1.6', fontSize: '15px' }}>
          <strong>🔧 核心优化：</strong><br/>
          ✅ 基于实际页面结构精确识别师门按钮<br/>
          ✅ 5种智能按钮查找策略，大幅提升成功率<br/>
          ✅ 优化页面加载等待机制<br/>
          ✅ 增强错误处理和诊断能力<br/>
          ✅ 支持多种按钮类型（button、input、submit）
        </div>
        {version && version.changelog && (
          <div style={{ marginTop: '15px', padding: '12px', background: 'rgba(255,255,255,0.8)', borderRadius: '8px' }}>
            <strong>📋 更新日志：</strong>
            <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
              {version.changelog.map((item, i) => (
                <li key={i} style={{ margin: '4px 0' }}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 统计信息 */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '25px' }}>
          <div style={{ background: 'rgba(255,255,255,0.95)', padding: '25px', borderRadius: '15px', boxShadow: '0 6px 25px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ width: '50px', height: '50px', background: 'linear-gradient(45deg, #667eea, #764ba2)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>👥</div>
              <div>
                <h3 style={{ margin: '0', fontSize: '28px', color: '#333' }}>{stats.total_accounts}</h3>
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>总账号数</p>
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.95)', padding: '25px', borderRadius: '15px', boxShadow: '0 6px 25px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ width: '50px', height: '50px', background: 'linear-gradient(45deg, #4facfe, #00f2fe)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>📊</div>
              <div>
                <h3 style={{ margin: '0', fontSize: '28px', color: '#333' }}>{stats.total_records}</h3>
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>总记录数</p>
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.95)', padding: '25px', borderRadius: '15px', boxShadow: '0 6px 25px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ width: '50px', height: '50px', background: 'linear-gradient(45deg, #f093fb, #f5576c)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>⚡</div>
              <div>
                <h3 style={{ margin: '0', fontSize: '28px', color: '#333' }}>v{version?.version || '2.1'}</h3>
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>优化版本</p>
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.95)', padding: '25px', borderRadius: '15px', boxShadow: '0 6px 25px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ width: '50px', height: '50px', background: 'linear-gradient(45deg, #ff9a9e, #fecfef)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>🎯</div>
              <div>
                <h3 style={{ margin: '0', fontSize: '28px', color: '#333' }}>{stats.crawl_status === 'running' ? '运行中' : '就绪'}</h3>
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>系统状态</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 师门数据表格 */}
      <div style={{ background: 'rgba(255,255,255,0.95)', borderRadius: '20px', padding: '25px', marginBottom: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 25px 0', color: '#333', fontSize: '22px' }}>🗂️ 师门爬虫数据 (优化版)</h2>
        {data.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'linear-gradient(45deg, #f8f9fa, #e9ecef)' }}>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>账号</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>序号</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>IP</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>类型</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>命名</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>等级</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>门派</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>次数/总次数</th>
                  <th style={{ padding: '15px', border: '1px solid #dee2e6', fontWeight: '600', fontSize: '14px' }}>状态</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, i) => (
                  <tr key={i} style={{ ':hover': { background: '#f8f9fa' } }}>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6', fontWeight: '500' }}>{item.account_username}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.sequence_number}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.ip}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.type}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.name}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.level}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>{item.guild}</td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6', color: '#667eea', fontWeight: 'bold', fontSize: '15px' }}>
                      {item.count_current}/{item.count_total}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid #dee2e6' }}>
                      <span style={{ 
                        padding: '6px 12px', 
                        borderRadius: '15px', 
                        background: item.status === '在线' ? '#d4edda' : item.status === '修炼中' ? '#fff3cd' : '#f8d7da',
                        color: item.status === '在线' ? '#155724' : item.status === '修炼中' ? '#856404' : '#721c24',
                        fontSize: '13px',
                        fontWeight: '500'
                      }}>
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>暂无师门数据，点击"生成演示数据"查看优化版效果</p>
          </div>
        )}
      </div>

      {/* 师门账号管理 */}
      <div style={{ background: 'rgba(255,255,255,0.95)', borderRadius: '20px', padding: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 25px 0', color: '#333', fontSize: '22px' }}>👥 师门账号管理 (优化版)</h2>
        {accounts.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {accounts.map((acc, i) => (
              <div key={i} style={{ 
                background: 'linear-gradient(135deg, #fff, #f8f9fa)', 
                padding: '25px', 
                borderRadius: '15px', 
                border: '2px solid #e9ecef',
                boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
                transition: 'transform 0.3s ease'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h4 style={{ margin: '0', color: '#333', fontSize: '18px' }}>{acc.username}</h4>
                  <span style={{ 
                    padding: '6px 12px', 
                    borderRadius: '15px', 
                    background: acc.status === 'active' ? '#d4edda' : '#f8d7da',
                    color: acc.status === 'active' ? '#155724' : '#721c24',
                    fontSize: '13px',
                    fontWeight: '500'
                  }}>
                    {acc.status === 'active' ? '活跃' : '非活跃'}
                  </span>
                </div>
                <p style={{ margin: '0 0 20px 0', color: '#666', fontSize: '14px' }}>
                  创建时间: {new Date(acc.created_at).toLocaleDateString()}
                </p>
                <button 
                  onClick={() => testOptimizedLogin(acc.username)}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: 'linear-gradient(45deg, #FF6B35, #F7931E)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '10px',
                    fontWeight: '600',
                    fontSize: '15px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.6 : 1,
                    boxShadow: '0 4px 15px rgba(255, 107, 53, 0.4)'
                  }}
                >
                  {loading ? '测试中...' : '🎯 师门登录优化测试'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px', color: '#666' }}>
            <p>暂无师门账号，点击"启动师门爬虫"创建优化版账号</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;