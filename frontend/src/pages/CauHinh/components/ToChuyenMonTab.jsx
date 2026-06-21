// src/pages/CauHinh/components/ToChuyenMonTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, TextField, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Box, Snackbar, Alert, CircularProgress
} from '@mui/material';
import { Add, Edit, Delete, Refresh } from '@mui/icons-material';
import { toChuyenMonAPI } from '../../../api/cauHinh';

const ToChuyenMonTab = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    ma_to: '',
    ten_to: '',
    mo_ta: '',
    active: true
  });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await toChuyenMonAPI.getAll();
      let items = [];
      if (response.data && response.data.items) {
        items = response.data.items;
      } else if (Array.isArray(response.data)) {
        items = response.data;
      } else {
        items = response.data || [];
      }
      setData(items);
    } catch (error) {
      console.error('Lỗi tải tổ chuyên môn:', error);
      showAlert('Lỗi tải dữ liệu', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        ma_to: item.ma_to || '',
        ten_to: item.ten_to || '',
        mo_ta: item.mo_ta || '',
        active: item.active !== undefined ? item.active : true
      });
    } else {
      setEditingItem(null);
      setFormData({
        ma_to: '',
        ten_to: '',
        mo_ta: '',
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await toChuyenMonAPI.update(editingItem.id, formData);
        showAlert('Cập nhật thành công', 'success');
      } else {
        await toChuyenMonAPI.create(formData);
        showAlert('Thêm mới thành công', 'success');
      }
      handleCloseDialog();
      fetchData();
    } catch (error) {
      showAlert('Lỗi: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc muốn xóa?')) {
      try {
        await toChuyenMonAPI.delete(id);
        showAlert('Xóa thành công', 'success');
        fetchData();
      } catch (error) {
        showAlert('Lỗi xóa: ' + (error.response?.data?.detail || error.message), 'error');
      }
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
  };

  const showAlert = (message, severity) => {
    setAlert({ open: true, message, severity });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Button variant="contained" startIcon={<Add />} onClick={() => handleOpenDialog()}>
          Thêm tổ chuyên môn
        </Button>
        <Button variant="outlined" startIcon={<Refresh />} onClick={fetchData}>
          Làm mới
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Mã tổ</TableCell>
              <TableCell>Tên tổ</TableCell>
              <TableCell>Mô tả</TableCell>
              <TableCell>Trạng thái</TableCell>
              <TableCell align="right">Thao tác</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">Không có dữ liệu</TableCell>
              </TableRow>
            ) : (
              data.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>{item.ma_to}</TableCell>
                  <TableCell>{item.ten_to}</TableCell>
                  <TableCell>{item.mo_ta || '-'}</TableCell>
                  <TableCell>
                    <span style={{ color: item.active ? 'green' : 'red', fontWeight: 'bold' }}>
                      {item.active ? '✅ Hoạt động' : '❌ Không hoạt động'}
                    </span>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleOpenDialog(item)}>
                      <Edit />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDelete(item.id)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Chỉnh sửa tổ chuyên môn' : 'Thêm tổ chuyên môn mới'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Mã tổ"
            value={formData.ma_to}
            onChange={(e) => setFormData({ ...formData, ma_to: e.target.value })}
            margin="dense"
            required
          />
          <TextField
            fullWidth
            label="Tên tổ"
            value={formData.ten_to}
            onChange={(e) => setFormData({ ...formData, ten_to: e.target.value })}
            margin="dense"
            required
          />
          <TextField
            fullWidth
            label="Mô tả"
            value={formData.mo_ta}
            onChange={(e) => setFormData({ ...formData, mo_ta: e.target.value })}
            margin="dense"
            multiline
            rows={2}
          />
          <Box mt={2}>
            <Button
              variant={formData.active ? 'contained' : 'outlined'}
              color={formData.active ? 'success' : 'default'}
              onClick={() => setFormData({ ...formData, active: !formData.active })}
            >
              {formData.active ? '✅ Hoạt động' : '❌ Không hoạt động'}
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Hủy</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingItem ? 'Cập nhật' : 'Thêm mới'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={alert.open} autoHideDuration={3000} onClose={() => setAlert({ ...alert, open: false })}>
        <Alert severity={alert.severity}>{alert.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default ToChuyenMonTab;