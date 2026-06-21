// src/pages/CauHinh/components/HocKyTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, TextField, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Box, Snackbar, Alert, CircularProgress,
  Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import { Add, Edit, Delete, Refresh } from '@mui/icons-material';
import { hocKyAPI, namHocAPI } from '../../../api/cauHinh';

const HocKyTab = () => {
  const [data, setData] = useState([]);
  const [namHocList, setNamHocList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    ten_hoc_ky: '',
    nam_hoc_id: '',
    so_thu_tu: 1,
    active: true
  });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchData();
    fetchNamHoc();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await hocKyAPI.getAll();
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
      console.error('Lỗi tải học kỳ:', error);
      showAlert('Lỗi tải dữ liệu', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchNamHoc = async () => {
    try {
      const response = await namHocAPI.getAll();
      let items = [];
      if (response.data && response.data.items) {
        items = response.data.items;
      } else if (Array.isArray(response.data)) {
        items = response.data;
      } else {
        items = response.data || [];
      }
      setNamHocList(items.filter(item => item.active));
    } catch (error) {
      console.error('Lỗi tải năm học:', error);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        ten_hoc_ky: item.ten_hoc_ky || '',
        nam_hoc_id: item.nam_hoc_id || '',
        so_thu_tu: item.so_thu_tu || 1,
        active: item.active !== undefined ? item.active : true
      });
    } else {
      setEditingItem(null);
      setFormData({
        ten_hoc_ky: '',
        nam_hoc_id: '',
        so_thu_tu: 1,
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await hocKyAPI.update(editingItem.id, formData);
        showAlert('Cập nhật thành công', 'success');
      } else {
        await hocKyAPI.create(formData);
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
        await hocKyAPI.delete(id);
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
          Thêm học kỳ
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
              <TableCell>Tên học kỳ</TableCell>
              <TableCell>Năm học</TableCell>
              <TableCell>Số thứ tự</TableCell>
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
                  <TableCell>{item.ten_hoc_ky}</TableCell>
                  <TableCell>{item.ten_nam_hoc || item.nam_hoc_id}</TableCell>
                  <TableCell>{item.so_thu_tu}</TableCell>
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
        <DialogTitle>{editingItem ? 'Chỉnh sửa học kỳ' : 'Thêm học kỳ mới'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Tên học kỳ"
            value={formData.ten_hoc_ky}
            onChange={(e) => setFormData({ ...formData, ten_hoc_ky: e.target.value })}
            margin="dense"
            required
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Năm học</InputLabel>
            <Select
              value={formData.nam_hoc_id}
              onChange={(e) => setFormData({ ...formData, nam_hoc_id: e.target.value })}
              label="Năm học"
            >
              {namHocList.map((item) => (
                <MenuItem key={item.id} value={item.id}>
                  {item.ten_nam_hoc}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Số thứ tự"
            type="number"
            value={formData.so_thu_tu}
            onChange={(e) => setFormData({ ...formData, so_thu_tu: parseInt(e.target.value) })}
            margin="dense"
            inputProps={{ min: 1, max: 3 }}
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

export default HocKyTab;