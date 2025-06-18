import { useState, useEffect } from 'react';
import { Table, Typography, Button } from 'antd';
import {
  ExclamationCircleOutlined,
  SearchOutlined,
  ToolOutlined,
  BulbOutlined,
  DeleteOutlined
} from '@ant-design/icons';

const { Title } = Typography;

interface WebDesignSuggestion {
  key: number;
  label: string;
  area: string;
  suggestion: string;
  reason: string;
}

export interface WebDesignProps {
  suggestions: WebDesignSuggestion[];
}

const WebDesign = (props: WebDesignProps) => {
  const [suggestions, setSuggestions] = useState<WebDesignSuggestion[]>([]);

  const fetchWebDevSuggestions = async () => {
    setSuggestions([]);
    try {
  
      const formattedSuggestions = props.suggestions.map((item: any) => ({
        key: item[0],
        label: item[0],
        area: item[2],
        suggestion: item[3],
        reason: item[4],
      }));

      setSuggestions(formattedSuggestions);
    } catch (err) {
      console.error(err);
      console.error('An error occurred while fetching web design suggestions.');
    }
  };

  useEffect(() => {
    fetchWebDevSuggestions();
  }, [props.suggestions]);

  const handleDelete = (key: number) => {
    setSuggestions(prev => prev.filter(item => item.key !== key));
    fetch('api/delete_webdesign_suggestion', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ webDesignSuggestionId: key, toDelete: "web_design_suggestion" }),
    })
      .then(response => {
        if (!response.ok) {
          console.error('Failed to delete web design suggestion.');
        }
      })
      .catch(err => {
        console.error('Error deleting web design suggestion:', err);
      });
  };

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
    {
      title: '',
      key: 'action',
      render: (_: any, record: WebDesignSuggestion) => (
        <Button
          type="text"
          onClick={() => handleDelete(record.key)}
          style={{
            visibility: 'hidden',
            padding: 0,
            fontWeight: 'bold',
            fontSize: '16px',
          }}
          className="inline-delete-button"
        >
          <DeleteOutlined />
        </Button>
      ),
      width: 50,
    },
  ];

  const exportToCSV = () => {
    if (!suggestions.length) return;

    const headers = ['Area', 'Suggestion', 'Reason'];
    const rows = suggestions.map(item => [
      `"${item.area.replace(/"/g, '""')}"`,
      `"${item.suggestion.replace(/"/g, '""')}"`,
      `"${item.reason.replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'web_design_suggestions.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

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

      <Table
        columns={columns}
        dataSource={suggestions}
        pagination={false}
        rowClassName={() => 'hoverable-row'}
        onRow={() => {
          return {
            onMouseEnter: (event) => {
              const button = event.currentTarget.querySelector('.inline-delete-button') as HTMLElement;
              if (button) button.style.visibility = 'visible';
            },
            onMouseLeave: (event) => {
              const button = event.currentTarget.querySelector('.inline-delete-button') as HTMLElement;
              if (button) button.style.visibility = 'hidden';
            },
          };
        }}
      />
    </div>
  );
};

export default WebDesign;
