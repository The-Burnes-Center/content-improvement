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

export default ContentClarity;