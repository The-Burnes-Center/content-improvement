
// created a table to show the content clarity suggestions
import { Table, Typography } from 'antd';
import { useState, useEffect } from 'react';

const { Paragraph } = Typography;

const ContentClarity = () => {
  
  interface Content {
    key: number;
    original: string;
    suggestion: string;
  }
  const [content, setContent] = useState<Content[]>([]);

  const handleAudit = async () => {
    try {
      const response = await fetch('api/content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: 'https://www.nj.gov/state/elections/vote.shtml',
        }),
      });

      const data = await response.json();
      console.log(data);
      const contentArray: Content[] = data.originalText.map((text: string, index: number) => ({
        key: index,
        original: text,
        suggestion: data.suggestions?.[index] || '',
      }));
      setContent(contentArray);

      //console.log(data);
      
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    handleAudit();
  }, []);

  // Combine content + suggestion into one row per entry
  const tableData = content.map((item ) => ({
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