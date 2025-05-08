
// created a table to show the content clarity suggestions
import { Table, Typography } from 'antd';
import { useState, useEffect } from 'react';

const { Paragraph } = Typography;

export interface ContentClarityProps {
  projectId: number | null;
}

const ContentClarity = (props: ContentClarityProps) => {
  
  interface Content {
    key: number;
    original: string;
    suggestion: string;
  }
  const [suggestions, setSuggestions] = useState<Content[]>([]);

  const fetchContentClaritySuggestions = async () => {
    setSuggestions([]);
    try {
      
      
      const auditResponse = await fetch(`api/get_content_clarity_audit?projectId=${props.projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        console.log("auditData", auditData)
        const contentClarityAuditId = auditData['content_clarity_audit'][0];

        console.log("contentClarityAuditId", contentClarityAuditId)

        const response = await fetch(`api/get_content_clarity_suggestions?contentClarityAuditId=${contentClarityAuditId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();

        console.log("data", data)
        console.log("response", response)
        if (response.ok) {
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

  useEffect(() => {
    fetchContentClaritySuggestions();
  }, []);

  // Combine content + suggestion into one row per entry
  const tableData = suggestions.map((item ) => ({
    key: item.key,
    original: item.original,
    suggestion: item.suggestion || 'No suggestions found.',
  }));

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
        <Paragraph style={{ whiteSpace: 'pre-wrap', backgroundColor: '#f6ffed', padding: '0.5rem', borderRadius: '6px' }}>
          {text}
        </Paragraph>
      ),
    },
  ];

  return (

    <div style={{ padding: '2rem' }}>
      <h2>Help users understand your content </h2>
      <Table
        columns={columns}
        dataSource={tableData}
        pagination={false}
        bordered
      />
    </div>
  );
};


export default ContentClarity;