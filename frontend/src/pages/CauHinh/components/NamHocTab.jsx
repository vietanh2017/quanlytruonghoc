// src/pages/CauHinh/components/NamHocTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, Box, CircularProgress, Alert, Typography
} from '@mui/material';
import { namHocAPI } from '../../../api/cauHinh';

const NamHocTab = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('✅ NamHocTab mounted');
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔵 Gọi API: /cauhinh/namhoc');
      const response = await namHocAPI.getAll();
      console.log('🟢 Response:', response.data);
      
      // Xử lý dữ liệu
      let items = [];
      if (response.data && response.data.items) {
        items = response.data.items;
      } else if (Array.isArray(response.data)) {
        items = response.data;
      } else {
        items = response.data || [];
      }
      
      console.log('📊 Dữ liệu:', items);
      setData(items);
    } catch (err) {
      console.error('🔴 Lỗi:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Box ml={2}>Đang tải dữ liệu...</Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Lỗi: {error}
        <Button onClick={fetchData} sx={{ ml: 2 }}>Thử lại</Button>
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Danh sách năm học ({data.length})</Typography>
        <Button variant="contained" onClick={() => alert('Thêm mới')}>
          Thêm năm học
        </Button>
        <Button variant="outlined" onClick={fetchData}>
          Làm mới
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Tên năm học</TableCell>
              <TableCell>Trạng thái</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} align="center" sx={{ py: 4 }}>
                  <Alert severity="info">⚠️ Chưa có dữ liệu</Alert>
                </TableCell>
              </TableRow>
            ) : (
              data.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>
                    {/* SỬA: ten_nao_hoc (trong DB) thay vì ten_nam_hoc */}
                    {item.ten_nao_hoc || item.ten_nam_hoc || 'Không có tên'}
                  </TableCell>
                  <TableCell>
                    <span style={{ color: item.active ? 'green' : 'red' }}>
                      {item.active ? '✅ Hoạt động' : '❌ Không hoạt động'}
                    </span>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default NamHocTab;