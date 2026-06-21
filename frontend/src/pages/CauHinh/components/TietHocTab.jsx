// src/pages/CauHinh/components/TietHocTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, TextField, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Box, Snackbar, Alert, CircularProgress
} from '@mui/material';
import { Add, Edit, Delete, Refresh } from '@mui/icons-material';
import { tietHocAPI } from '../../../api/cauHinh';

const TietHocTab = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    so_thu_tu: 1,
    ten_tiet: '',
    thoi_gian_bat_dau: '',
    thoi_gian_ket_thuc: '',
    active: 1
  });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await tietHocAPI.getAll();
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
      console.error('Lỗi tải tiết học:', error);
      showAlert('Lỗi tải dữ liệu', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        so_thu_tu: item.so_thu_tu || 1,
        ten_tiet: item.ten_tiet || '',
        thoi_gian_bat_dau: item.thoi_gian_bat_dau || '',
        thoi_gian_ket_thuc: item.thoi_gian_ket_thuc || '',
        active: item.active !== undefined ? item.active : 1
      });
    } else {
      setEditingItem(null);
      setFormData({
        so_thu_tu: data.length + 1,
        ten_tiet: '',
        thoi_gian_bat_dau: '',
        thoi_gian_ket_thuc: '',
        active: 1
      });
    }
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await tietHocAPI.update(editingItem.id, formData);
        showAlert('Cập nhật thành công', 'success');
      } else {
        await tietHocAPI.create(formData);
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
        await tietHocAPI.delete(id);
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
          Thêm tiết học
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
              <TableCell>Số thứ tự</TableCell>
              <TableCell>Tên tiết</TableCell>
              <TableCell>Thời gian bắt đầu</TableCell>
              <TableCell>Thời gian kết thúc</TableCell>
              <TableCell>Trạng thái</TableCell>
              <TableCell align="right">Thao tác</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">Không có dữ liệu</TableCell>
              </TableRow>
            ) : (
              data.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>{item.so_thu_tu}</TableCell>
                  <TableCell>{item.ten_tiet}</TableCell>
                  <TableCell>{item.thoi_gian_bat_dau}</TableCell>
                  <TableCell>{item.thoi_gian_ket_thuc}</TableCell>
                  <TableCell>
                    <span style={{ color: item.active === 1 ? 'green' : 'red', fontWeight: 'bold' }}>
                      {item.active === 1 ? '✅ Hoạt động' : '❌ Không hoạt động'}
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
        <DialogTitle>{editingItem ? 'Chỉnh sửa tiết học' : 'Thêm tiết học mới'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Số thứ tự"
            type="number"
            value={formData.so_thu_tu}
            onChange={(e) => setFormData({ ...formData, so_thu_tu: parseInt(e.target.value) })}
            margin="dense"
            required
            inputProps={{ min: 1 }}
          />
          <TextField
            fullWidth
            label="Tên tiết học"
            value={formData.ten_tiet}
            onChange={(e) => setFormData({ ...formData, ten_tiet: e.target.value })}
            margin="dense"
            required
          />
          <TextField
            fullWidth
            label="Thời gian bắt đầu"
            placeholder="07:30"
            value={formData.thoi_gian_bat_dau}
            onChange={(e) => setFormData({ ...formData, thoi_gian_bat_dau: e.target.value })}
            margin="dense"
          />
          <TextField
            fullWidth
            label="Thời gian kết thúc"
            placeholder="08:15"
            value={formData.thoi_gian_ket_thuc}
            onChange={(e) => setFormData({ ...formData, thoi_gian_ket_thuc: e.target.value })}
            margin="dense"
          />
          <Box mt={2}>
            <Button
              variant={formData.active === 1 ? 'contained' : 'outlined'}
              color={formData.active === 1 ? 'success' : 'default'}
              onClick={() => setFormData({ ...formData, active: formData.active === 1 ? 0 : 1 })}
            >
              {formData.active === 1 ? '✅ Hoạt động' : '❌ Không hoạt động'}
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

export default TietHocTab;