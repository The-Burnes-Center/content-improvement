import React from 'react';
import { Table, Typography } from 'antd';
import {
  ExclamationCircleOutlined,
  SearchOutlined,
  ToolOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

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

const data = [
  {
    key: '1',
    area: 'Header area',
    suggestion: 'Minimize height or make sticky',
    reason: 'Too tall, pushes content too far down',
  },
  {
    key: '2',
    area: 'Important Notices (red box)',
    suggestion: 'Use collapsible alerts or accordion style',
    reason: 'Wall of text overwhelms user, important info can be missed',
  },
  {
    key: '3',
    area: 'Button Grid',
    suggestion: 'Use icons and better grouping by user type (e.g., student, voter, poll worker)',
    reason: 'Improves scannability and relevance',
  },
  {
    key: '4',
    area: 'Poll Worker Callout',
    suggestion: 'Add an image or badge for visual appeal',
    reason: 'Text alone doesn’t draw attention',
  },
  {
    key: '5',
    area: '"Sign Up for Updates" bar',
    suggestion: 'Make it a popup or reposition higher',
    reason: 'Users might miss it; it’s key engagement',
  },
  {
    key: '6',
    area: 'Footer area',
    suggestion: 'Collapse sections into accordion or tabbed format',
    reason: 'Extremely dense and repetitive; hard to find key links',
  },
  {
    key: '7',
    area: 'Color usage',
    suggestion: 'Use more contrast between card backgrounds and white',
    reason: 'Everything blends together — harder to focus attention',
  },
  {
    key: '8',
    area: 'Mobile-friendliness',
    suggestion: 'Add spacing, simplify columns',
    reason: 'On smaller screens this will likely be overwhelming',
  },
];

const WebDesign = () => {
  return (
    <div style={{ padding: '1rem' }}>
      <Title level={4}>
        <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: '0.5rem' }} />
        Suggested Improvements (with reasoning)
      </Title>
      <Table columns={columns} dataSource={data} pagination={false} />
    </div>
  );
};

export default WebDesign;
