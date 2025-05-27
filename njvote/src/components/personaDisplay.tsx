import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';
import type { TableColumnsType, TableProps } from 'antd';
import { Table } from 'aws-sdk/clients/glue';


export interface PersonaDisplayProps {
  persona: string | undefined;
  id: number | undefined;
  updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
  displayItems: string;
  loading: boolean
}

interface TableType {
    key: string;
    item: string;
}

const PersonaDisplay = (props: PersonaDisplayProps) => {

    const [displayItems, setDisplayItems] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    useEffect(() => {
        setDisplayItems(["item1", "item2", "item3"]);
        setLoading(props.loading);
    }, [props.persona, props.displayItems, props.loading]);


    const columns: TableColumnsType<TableType> = [
        {
            title: 'item',
            dataIndex: 'item',
            width: '100%',
            render: (text) => <span style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{text}</span>,
        },
    ];



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
                            
                        </>}
                </div>
            </div>
        </>
    );
};

export default PersonaDisplay;