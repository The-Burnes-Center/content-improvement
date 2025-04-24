import { Row, Col, Card } from 'antd';
import { useState, useEffect } from 'react';


const ContentClarity = () => {

  const [content, setContent] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

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
          }).then(rsp => rsp.json()).then(rsp => {
            console.log(rsp)
            setContent(rsp.oringalText);
            setSuggestions(rsp.suggestions);
          })
      } catch (err) {
          console.error(err);
      }
    };
  
    useEffect(() => {
      handleAudit();
    }, []);

    return (
        <div style={{ padding: '2rem' }}>
          <Row gutter={24}>
            {/* Old Content Column */}
            <Col span={12}>
              <Card
                title="Original Website Content"
                style={{ minHeight: '400px' }}
              >
                {content.map((item, index) => (
                  <p key={index}>
                    {item}
                  </p>
                ))}
              </Card>
            </Col>
    
            {/* Suggested Improvements Column */}
            <Col span={12}>
              <Card
                title="Suggested Improvements"
                style={{ minHeight: '400px', backgroundColor: '#f6ffed' }}
              >
                {suggestions.map((item, index) => (
                  <p key={index}>
                    {item}
                  </p>
                ))}
              </Card>
            </Col>
          </Row>
        </div>
      );
}

export default ContentClarity;