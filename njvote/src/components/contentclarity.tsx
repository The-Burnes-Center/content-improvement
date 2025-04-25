<<<<<<< Updated upstream
import { Row, Col, Card } from 'antd';

const ContentClarity = () => {
    return (
        <div style={{ padding: '2rem' }}>
          <Row gutter={24}>
            {/* Old Content Column */}
            <Col span={12}>
              <Card
                title="Original Website Content"
                style={{ minHeight: '400px' }}
              >
              </Card>
            </Col>
    
            {/* Suggested Improvements Column */}
            <Col span={12}>
              <Card
                title="Suggested Improvements"
                style={{ minHeight: '400px', backgroundColor: '#f6ffed' }}
              >
                <p>
                  ✅ Clear call-to-action buttons for voter registration.<br />
                  ✅ Integrated search bar for FAQs and resources.<br />
                  ✅ Highlighted help section with chatbot support.<br />
                  ✅ Modern layout with accessibility enhancements.
                </p>
              </Card>
            </Col>
          </Row>
        </div>
      );
}
=======
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
>>>>>>> Stashed changes

export default ContentClarity;