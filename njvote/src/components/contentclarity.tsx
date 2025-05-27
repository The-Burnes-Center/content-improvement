// Ant Design components and React imports
import { Table, Typography, Button, TableProps } from 'antd';
import { useState, useEffect } from 'react';
import type { ColumnsType } from 'antd/es/table';


const { Paragraph } = Typography;

// Props interface definition
export interface ContentClarityProps {
  projectId: number | null;
}

const ContentClarity = ({ projectId }: ContentClarityProps) => {
  // Local interface to shape suggestion data
  interface Content {
    key: number;
    area: string;
    original: string;
    suggestion: string;
  }

  // State to hold fetched suggestions
  const [suggestions, setSuggestions] = useState<Content[]>([]);

  // Function to fetch suggestions for content clarity
  const fetchContentClaritySuggestions = async () => {
    setSuggestions([]);

    try {
      // First, get the audit ID for the current project
      const auditResponse = await fetch(
        `api/get_content_clarity_audit?projectId=${projectId}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!auditResponse.ok) {
        console.error('Failed to fetch content clarity audit.');
        return;
      }

      const auditData = await auditResponse.json();
      const contentClarityAuditId = auditData['content_clarity_audit'][0];

      // Then, use the audit ID to get the suggestions
      const response = await fetch(
        `api/get_content_clarity_suggestions?contentClarityAuditId=${contentClarityAuditId}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) {
        console.error('Failed to fetch content clarity suggestions.');
        return;
      }

      const data = await response.json();

      // Transform raw API response into component-friendly structure
      const transformed = data['suggestions'].map((item: any, index: number) => ({
        key: index,
        original: item[2],
        suggestion: item[3],
        area: item[4],
      }));

      console.log(transformed)

      setSuggestions(transformed);
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

  // Define table columns
  const columns: ColumnsType<Content> = [
    {
      title: 'Area of Improvement',
      dataIndex: 'area',
      key: 'area',
      render: (text: string) => (
        <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{text}</Paragraph>
      ),
      onFilter: (value: boolean | React.Key, record: Content) => record.area.toLowerCase().includes(String(value).toLowerCase()),
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
