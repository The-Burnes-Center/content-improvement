import { useState, useEffect } from 'react';
import { Table, Typography } from 'antd';
import {
  ExclamationCircleOutlined,
  SearchOutlined,
  ToolOutlined,
  BulbOutlined,
} from '@ant-design/icons';


const { Title } = Typography;

interface WebDesignSuggestion {
  label: string;
  area:string;
  suggestion: string;
  reason: string;

}
  const WebDesign = () => {
    const [suggestions, setSuggestions] = useState<WebDesignSuggestion[]>([]);
    const handleAudit = async () => {
      try {
          const response = await fetch('/api/webdesign', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  url: 'https://www.nj.gov/state/elections/vote.shtml',
              }),
            });
            const data = await response.json();
            console.log("Fetched data:", data);
            
      
            if (Array.isArray(data)) {
              const withKeys = data.map(item => ({
                ...item,
                key: item.key.toString(), // Convert int -> string for AntD
              }));
              setSuggestions(withKeys);
            } else {
              console.error("Unexpected response format:", data);
            }
          } catch (err) {
            console.error("Error fetching audit:", err);
          }
        };
        useEffect(() => {
          handleAudit();
        }, []);
              
const columns = [
  {
    title: (
      <span>
        <SearchOutlined /> Area
      </span>
    ),
    dataIndex: 'area',
    key: 'area',
    render: (text: string) => <strong>{text}</strong>,
  },
  {
    title: (
      <span>
        <ToolOutlined /> Suggestion
      </span>
    ),
    dataIndex: 'suggestion',
    key: 'suggestion',
  },
  {
    title: (
      <span>
        <BulbOutlined /> Reason
      </span>
    ),
    dataIndex: 'reason',
    key: 'reason',
  },
];

  return (
    <div style={{ padding: '1rem' }}>
      <Title level={4}>
        <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: '0.5rem' }} />
        Suggested Improvements (with reasoning)
      </Title>
      <Table columns={columns} dataSource={suggestions} pagination={false} />
    </div>
  );
};

export default WebDesign;
