import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import type { TableColumnsType, TableProps } from 'antd';
import { Table } from 'antd';

type TableRowSelection<T extends object = object> = TableProps<T>['rowSelection'];


export interface PersonaDisplayProps {
  persona: string | undefined;
  id: number | undefined;
  updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
  positives: string;
  challenges: string;
  loading: boolean
}

interface TableType {
    key: string;
    item: string;
}

const PersonaDisplay = (props: PersonaDisplayProps) => {

    const [displayItemsPos, setDisplayItemsPos] = useState<string[]>([]);
    const [displayItemsNeg, setDisplayItemsNeg] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedRowKeysPos, setSelectedRowKeysPos] = useState<React.Key[]>([]);
    const [selectedRowKeysNeg, setSelectedRowKeysNeg] = useState<React.Key[]>([]);

    useEffect(() => {
        setDisplayItemsPos(props.positives ? props.positives.split('\n').filter(item => item.trim() !== '') : []);
        setDisplayItemsNeg(props.challenges ? props.challenges.split('\n').filter(item => item.trim() !== '') : []);
        setLoading(props.loading);
    }, [props.persona, props.positives, props.challenges, props.loading]);


    const columns: TableColumnsType<TableType> = [
        {
            title: 'item',
            dataIndex: 'item',
            width: '100%',
            render: (text) => <span style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{text}</span>,
        },
    ];

    const tableDataPos = Array.from({ length: displayItemsPos.length }, (_: any, index: number) => ({
        key: index.toString(),
        item: displayItemsPos[index],
    }));

    const onSelectChangePos = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeysPos(newSelectedRowKeys);
    };

    const rowSelectionPos: TableRowSelection<TableType> = {
        selectedRowKeys: selectedRowKeysPos,
        onChange: onSelectChangePos,
    };

    const tableDataNeg = Array.from({ length: displayItemsNeg.length }, (_: any, index: number) => ({
        key: index.toString(),
        item: displayItemsNeg[index],
    }));

    const onSelectChangeNeg = (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeysNeg(newSelectedRowKeys);
    };

    const rowSelectionNeg: TableRowSelection<TableType> = {
        selectedRowKeys: selectedRowKeysNeg,
        onChange: onSelectChangeNeg,
    };

    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2%' }}>
                <div
                    className='grayBox'
                    style={{
                        flex: 1, 
                        width: '37rem',
                        height: '25rem',
                        overflowY: 'auto',
                        marginLeft: '2%',
                        marginTop: '-0.03rem', 
                        padding: '1rem',
                        backgroundColor: 'white',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word',  
                        display: 'block',
                        font: '13px "Helvetica Neue"'
                 
                    }}>
                        {loading ? <LoadingOutlined /> : 
                        
                        <>
                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <div style={{ flex: 1 }}>
                                    <Table<TableType>
                                    rowSelection={rowSelectionPos}
                                    columns={columns}
                                    dataSource={tableDataPos}
                                    pagination={false}
                                    />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <Table<TableType>
                                    rowSelection={rowSelectionNeg}
                                    columns={columns}
                                    dataSource={tableDataNeg}
                                    pagination={false}
                                    />
                                </div>
                            </div>
                        </>}
                </div>
            </div>
        </>
    );
};

export default PersonaDisplay;