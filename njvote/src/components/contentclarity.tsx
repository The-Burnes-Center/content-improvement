// Ant Design components and React imports
import { Table, Typography, Button, TableProps, Tooltip } from 'antd';
import { useState, useEffect } from 'react';
import type { ColumnsType } from 'antd/es/table';
import { DeleteOutlined } from '@ant-design/icons';

const { Paragraph } = Typography;

interface Content {
  key: number;
  area: string;
  original: string;
  suggestion: string;
}

// Props interface definition
export interface ContentClarityProps {
  suggestions?: Content[];
}

const ContentClarity = (props: ContentClarityProps) => {
  // Local interface to shape suggestion data

  // State to hold fetched suggestions
  const [suggestions, setSuggestions] = useState<Content[]>([]);
  const [hoveredRowKey, setHoveredRowKey] = useState<number | null>(null);


  // Function to fetch suggestions for content clarity
  const fetchContentClaritySuggestions = async () => {
    setSuggestions([]);

    try {
      // Transform raw API response into component-friendly structure
      const transformed = props.suggestions?.map((item: any) => ({
        key: item[0],
        original: item[2],
        suggestion: item[3],
        area: item[4],
        dismissed: item[1],
      }));

      setSuggestions(transformed ? transformed : []);
    } catch (err) {
      console.error('An error occurred while fetching content clarity suggestions.', err);
    }
  };

  // Trigger the fetch once the component is mounted
  useEffect(() => {
    fetchContentClaritySuggestions();
  }, []);

  // Format data for the table component
  const tableData = suggestions.map((item) => ({
    key: item.key,
    area: item.area,
    original: item.original,
    suggestion: item.suggestion || 'No suggestions found.',
  }));

  const onChange: TableProps<Content>['onChange'] = (
    pagination: any,
    filters: any,
    sorter: any,
    extra: any
    ) => {
      console.log('params', pagination, filters, sorter, extra);
    };

  const handleDelete = (areaToDelete: number) => {
    setSuggestions(prev => prev.filter(item => item.key !== areaToDelete));
    fetch('https://a8b6filf5e.execute-api.us-east-1.amazonaws.com/delete', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contentClaritySuggestionId: areaToDelete, toDelete: "content_suggestion" }),
    })
      .then((res) => {
      if (!res.ok) {
        throw new Error('Failed to delete suggestion');
      }
      })
      .catch((err) => {
      console.error('Error deleting suggestion:', err);
      });
  };

  const columns: ColumnsType<Content> = [
    {
      title: 'Area of Improvement',
      dataIndex: 'area',
      key: 'area',
      render: (text: string, record: Content) => (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '8px',
          }}
          onMouseEnter={() => setHoveredRowKey(record.key)}
          onMouseLeave={() => setHoveredRowKey(null)}
        >
          <Paragraph style={{ whiteSpace: 'pre-wrap', marginBottom: 0 }}>
            {text}
          </Paragraph>
          {hoveredRowKey === record.key && (
            <Tooltip title="Dismiss Suggestion">
              <Button
                type="text"
                icon={<DeleteOutlined />}
                size="small"
                style={{ opacity: 1 }}
                onClick={() => handleDelete(record.key)}
              />
            </Tooltip>
          )}
        </div>
      ),
      onFilter: (value: boolean | React.Key, record: Content) =>
        record.area.toLowerCase().includes(String(value).toLowerCase()),
      filters: Array.from(new Set(suggestions.map(item => item.area))).map(area => ({
        text: area,
        value: area,
      })),
      filterSearch: true,
      width: '40%',
    },
    {
      title: 'Original Content',
      dataIndex: 'original',
      key: 'original',
      render: (text: string) => (
        <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{text}</Paragraph>
      ),
    },
    {
      title: 'Suggested Improvement(s)',
      dataIndex: 'suggestion',
      key: 'suggestion',
      render: (text: string) => (
        <Paragraph
          style={{
            whiteSpace: 'pre-wrap',
            backgroundColor: '#f6ffed',
            padding: '0.5rem',
            borderRadius: '6px',
          }}
        >
          {text}
        </Paragraph>
      ),
    },
  ];


  // Export suggestions to a downloadable CSV file
  const exportToCSV = () => {
    if (!suggestions.length) return;

    const headers = ['Original Content', 'Suggested Improvement'];
    const rows = suggestions.map((item) => [
      `"${item.original.replace(/"/g, '""')}"`,
      `"${item.suggestion.replace(/"/g, '""')}"`,
    ]);

    const csvContent = [headers, ...rows].map((e) => e.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'content_clarity_suggestions.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Render component
  return (
  <div style={{ marginLeft: '1rem'}}>
      <div style={{ padding: '1rem'}}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ marginLeft: '0.1rem', marginBottom: '1rem'  }}>Help users understand your content</h2>
          <Button type="primary" onClick={exportToCSV}>
            Export to CSV
          </Button>
        </div>
        <Table
          columns={columns}
          onChange={onChange}
          dataSource={tableData}
          pagination={{pageSize: 4}}
          bordered
        />
        
      </div>
    </div>
  );
};

export default ContentClarity;
