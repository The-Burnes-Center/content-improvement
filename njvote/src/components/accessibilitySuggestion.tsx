import { useState, useEffect } from 'react';
import { Table, Typography, Button } from 'antd';
import {
  ExclamationCircleOutlined,
  SearchOutlined,
  ToolOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

// Define the shape of a single suggestion item
interface WebDesignSuggestion {
  label: string;
  area: string;
  suggestion: string;
  reason: string;
}

export interface WebDesignProps {
  projectId: number | null;
}

const WebDesign = ({ projectId }: WebDesignProps) => {
  const [suggestions, setSuggestions] = useState<WebDesignSuggestion[]>([]);

  // Fetches suggestions based on projectId
  const fetchWebDevSuggestions = async () => {
    setSuggestions([]);

    if (!projectId) return;

    try {
      // First fetch the audit ID for the project
      const auditResponse = await fetch(`api/get_webdesign_audit?projectId=${projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!auditResponse.ok) {
        console.error('Failed to fetch web design audit.');
        return;
      }

      const auditData = await auditResponse.json();
      const webDesignAuditId = auditData['web_design_audit'][0];

      // Then fetch the suggestions using the audit ID
      const response = await fetch(`api/get_webdesign_suggestions?webDesignAuditId=${webDesignAuditId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        console.error('Failed to fetch web design suggestions.');
        return;
      }

      const data = await response.json();

      // Transform the response data into the expected format
      const parsedSuggestions = data['suggestions'].map((item: any) => ({
        label: item[0],
        area: item[2],
        suggestion: item[3],
        reason: item[4],
      }));

      setSuggestions(parsedSuggestions);
    } catch (err) {
      console.error('An error occurred while fetching web design suggestions.', err);
    }
  };

  // Refetch suggestions whenever the projectId changes
  useEffect(() => {
    fetchWebDevSuggestions();
  }, [projectId]);

  // Table column configuration
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

  // Export suggestions to a CSV file
  const exportToCSV = () => {
    if (!suggestions.length) return;

    const headers = ['Area', 'Suggestion', 'Reason'];
    const rows = suggestions.map((item) => [
      `"${item.area.replace(/"/g, '""')}"`,
      `"${item.suggestion.replace(/"/g, '""')}"`,
      `"${item.reason.replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers, ...rows].map((r) => r.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'web_design_suggestions.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Component render
  return (
    <div style={{ padding: '1rem' }}>
      <h2 style={{ marginBottom: '1rem' }}>Improve the placement of your content</h2>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: '0.5rem' }} />
          Suggested Improvements (with reasoning)
        </Title>

        <Button type="primary" onClick={exportToCSV}>
          Export to CSV
        </Button>
      </div>

      <Table columns={columns} dataSource={suggestions} pagination={false} />
    </div>
  );
};

export default WebDesign;
