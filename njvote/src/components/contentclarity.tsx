// Ant Design components and React imports
import { Table, Typography, Button } from 'antd';
import { useState, useEffect } from 'react';

const { Paragraph } = Typography;

// Props interface definition
export interface ContentClarityProps {
  projectId: number | null;
}

const ContentClarity = (props: ContentClarityProps) => {

  // Local interface to shape suggestion data
  interface Content {
    key: number;
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
      const auditResponse = await fetch(`api/get_content_clarity_audit?projectId=${props.projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        console.log("auditData", auditData);
        const contentClarityAuditId = auditData['content_clarity_audit'][0];
        console.log("contentClarityAuditId", contentClarityAuditId);

        // Then, use the audit ID to get the suggestions
        const response = await fetch(`api/get_content_clarity_suggestions?contentClarityAuditId=${contentClarityAuditId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();
        console.log("data", data);
        console.log("response", response);

        if (response.ok) {
          // Transform raw API response into component-friendly structure
          const suggestions = data['suggestions'].map((item: any) => ({
            original: item[2],
            suggestion: item[3],
          }));
          setSuggestions(suggestions);
        } else {
          console.error('Failed to fetch content clarity suggestions.');
        }
      } else {
        console.error('Failed to fetch content clarity audit.');
      }
    } catch (err) {
      console.error(err);
      console.error('An error occurred while fetching content clarity suggestions.');
    }
  };

  // Trigger the fetch once the component is mounted
  useEffect(() => {
    fetchContentClaritySuggestions();
  }, []);

  // Format data for the table component
  const tableData = suggestions.map((item) => ({
    key: item.key,
    original: item.original,
    suggestion: item.suggestion || 'No suggestions found.',
  }));

  // Define table columns
  const columns = [
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
        <Paragraph style={{
          whiteSpace: 'pre-wrap',
          backgroundColor: '#f6ffed',
          padding: '0.5rem',
          borderRadius: '6px'
        }}>
          {text}
        </Paragraph>
      ),
    },
  ];

  // Export suggestions to a downloadable CSV file
  const exportToCSV = () => {
    if (!suggestions.length) return;

    const headers = ['Original Content', 'Suggested Improvement'];
    const rows = suggestions.map(item => [
      `"${item.original.replace(/"/g, '""')}"`,
      `"${item.suggestion.replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers, ...rows].map(e => e.join(',')).join('\n');
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
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ marginBottom: 0 }}>Help users understand your content</h2>
        <Button type="primary" onClick={exportToCSV}>
          Export to CSV
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={tableData}
        pagination={{ pageSize: 4 }}
        bordered
      />
    </div>
  );
};

export default ContentClarity;
