// src/pages/CauHinh/components/NguoiDungTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, TextField, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Box, Snackbar, Alert, CircularProgress,
  Select, MenuItem, FormControl, InputLabel, Chip
} from '@mui/material';
import { Add, Edit, Delete, Refresh, VpnKey } from '@mui/icons-material';
import { nguoiDungAPI } from '../../../api/cauHinh';

const NguoiDungTab = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [openResetDialog, setOpenResetDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [resetUserId, setResetUserId] = useState(null);
  const [resetPassword, setResetPassword] = useState('eduschool@123');
  const [formData, setFormData] = useState({
    ho_ten: '',
    email: '',
    role: 'GV',
    mat_khau: '',
    active: true
  });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  const roleOptions = [
    { value: 'ADMIN', label: 'Admin' },
    { value: 'GV', label: 'Giáo viên' },
    { value: 'NV', label: 'Nhân viên' },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await nguoiDungAPI.getAll();
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
      console.error('Lỗi tải người dùng:', error);
      showAlert('Lỗi tải dữ liệu', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        ho_ten: item.ho_ten || '',
        email: item.email || '',
        role: item.role || 'GV',
        mat_khau: '',
        active: item.active !== undefined ? item.active : true
      });
    } else {
      setEditingItem(null);
      setFormData({
        ho_ten: '',
        email: '',
        role: 'GV',
        mat_khau: '',
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleOpenResetDialog = (id) => {
    setResetUserId(id);
    setResetPassword('eduschool@123');
    setOpenResetDialog(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        const submitData = { ...formData };
        delete submitData.mat_khau;
        await nguoiDungAPI.update(editingItem.id, submitData);
        showAlert('Cập nhật thành công', 'success');
      } else {
        await nguoiDungAPI.create(formData);
        showAlert('Thêm mới thành công', 'success');
      }
      handleCloseDialog();
      fetchData();
    } catch (error) {
      showAlert('Lỗi: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const handleResetPassword = async () => {
    try {
      await nguoiDungAPI.resetPassword(resetUserId, resetPassword);
      showAlert(`Đặt lại mật khẩu thành công: ${resetPassword}`, 'success');
      setOpenResetDialog(false);
    } catch (error) {
      showAlert('Lỗi: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc muốn xóa?')) {
      try {
        await nguoiDungAPI.delete(id);
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

  const getRoleLabel = (role) => {
    const found = roleOptions.find(r => r.value === role);
    return found ? found.label : role;
  };

  const getRoleColor = (role) => {
    switch(role) {
      case 'ADMIN': return 'error';
      case 'GV': return 'primary';
      case 'NV': return 'warning';
      default: return 'default';
    }
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
          Thêm người dùng
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
              <TableCell>Họ tên</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Vai trò</TableCell>
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
                  <TableCell>{item.ho_ten}</TableCell>
                  <TableCell>{item.email}</TableCell>
                  <TableCell>
                    <Chip 
                      label={getRoleLabel(item.role)} 
                      color={getRoleColor(item.role)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <span style={{ color: item.active ? 'green' : 'red', fontWeight: 'bold' }}>
                      {item.active ? '✅ Hoạt động' : '❌ Không hoạt động'}
                    </span>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleOpenDialog(item)}>
                      <Edit />
                    </IconButton>
                    <IconButton color="warning" onClick={() => handleOpenResetDialog(item.id)}>
                      <VpnKey />
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

      {/* Dialog Thêm/Sửa */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Họ tên"
            value={formData.ho_ten}
            onChange={(e) => setFormData({ ...formData, ho_ten: e.target.value })}
            margin="dense"
            required
          />
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            margin="dense"
            required
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Vai trò</InputLabel>
            <Select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              label="Vai trò"
            >
              {roleOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {!editingItem && (
            <TextField
              fullWidth
              label="Mật khẩu"
              type="password"
              value={formData.mat_khau}
              onChange={(e) => setFormData({ ...formData, mat_khau: e.target.value })}
              margin="dense"
              helperText="Để trống sẽ dùng mặc định: eduschool@123"
            />
          )}
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

      {/* Dialog Reset Password */}
      <Dialog open={openResetDialog} onClose={() => setOpenResetDialog(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Đặt lại mật khẩu</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Mật khẩu mới"
            type="text"
            value={resetPassword}
            onChange={(e) => setResetPassword(e.target.value)}
            margin="dense"
            helperText="Mặc định: eduschool@123"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenResetDialog(false)}>Hủy</Button>
          <Button onClick={handleResetPassword} variant="contained" color="warning">
            Đặt lại
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={alert.open} autoHideDuration={3000} onClose={() => setAlert({ ...alert, open: false })}>
        <Alert severity={alert.severity}>{alert.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default NguoiDungTab;