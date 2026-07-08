// frontend/src/pages/CauHinh/components/MonHocTab.jsx
import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Button, TextField, Dialog, DialogActions, DialogContent,
  DialogTitle, IconButton, Box, Snackbar, Alert, CircularProgress,
  Switch, FormControlLabel, Select, MenuItem, InputLabel, FormControl,
  Chip, Tabs, Tab, Typography, Divider, Grid
} from '@mui/material';
import { Add, Edit, Delete, Refresh, AddCircle, RemoveCircle } from '@mui/icons-material';
import axios from 'axios';
import { monHocAPI, phanMonAPI, soTietAPI } from '../../../api/cauHinh';

const MonHocTab = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [formData, setFormData] = useState({
    ma_mon: '',
    ten_mon: '',
    co_phan_mon: false,
    to_id: '',
    thu_tu: 0,
    active: true,
    phan_mon_list: [],
    khoi_list: []
  });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });
  const [toList, setToList] = useState([]);

  const KHOI_LIST = [6, 7, 8, 9];

  useEffect(() => {
    fetchData();
    fetchToList();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await monHocAPI.getAll();
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
      console.error('Lỗi tải môn học:', error);
      showAlert('Lỗi tải dữ liệu', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchToList = async () => {
    try {
      const response = await axios.get(API_URL + '/api/v1/cau-hinh/to-chuyen-mon');
      setToList(response.data || []);
    } catch (error) {
      console.error('Lỗi tải tổ chuyên môn:', error);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        id: item.id,
        ma_mon: item.ma_mon || '',
        ten_mon: item.ten_mon || '',
        co_phan_mon: item.co_phan_mon || false,
        to_id: item.to_id || '',
        thu_tu: item.thu_tu || 0,
        active: item.active !== undefined ? item.active : true,
        phan_mon_list: item.phan_mon_list || [],
        khoi_list: item.khoi_list && item.khoi_list.length > 0
          ? item.khoi_list
          : KHOI_LIST.map(k => ({ khoi: k, so_tiet: 0 }))
      });
    } else {
      setEditingItem(null);
      setFormData({
        ma_mon: '',
        ten_mon: '',
        co_phan_mon: false,
        to_id: '',
        thu_tu: 0,
        active: true,
        phan_mon_list: [],
        khoi_list: KHOI_LIST.map(k => ({ khoi: k, so_tiet: 0 }))
      });
    }
    setTabValue(0);
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    try {
      if (!formData.ma_mon.trim()) {
        showAlert('Vui lòng nhập mã môn học', 'error');
        return;
      }
      if (!formData.ten_mon.trim()) {
        showAlert('Vui lòng nhập tên môn học', 'error');
        return;
      }

      const submitData = {
        ma_mon: formData.ma_mon.trim(),
        ten_mon: formData.ten_mon.trim(),
        co_phan_mon: formData.co_phan_mon,
        to_id: formData.to_id || null,
        thu_tu: formData.thu_tu || 0,
        active: formData.active
      };

      let result;
      if (editingItem) {
        result = await monHocAPI.update(editingItem.id, submitData);
        showAlert('Cập nhật môn học thành công', 'success');

        if (formData.khoi_list && formData.khoi_list.length > 0) {
          await soTietAPI.deleteByMonHoc(editingItem.id);
          for (const item of formData.khoi_list) {
            if (item.so_tiet > 0) {
              await soTietAPI.create({
                mon_hoc_id: editingItem.id,
                khoi: item.khoi,
                so_tiet: item.so_tiet
              });
            }
          }
        }
      } else {
        result = await monHocAPI.create(submitData);
        showAlert('Thêm môn học thành công', 'success');

        if (formData.khoi_list && formData.khoi_list.length > 0) {
          const newMonHoc = result.data;
          for (const item of formData.khoi_list) {
            if (item.so_tiet > 0) {
              await soTietAPI.create({
                mon_hoc_id: newMonHoc.id,
                khoi: item.khoi,
                so_tiet: item.so_tiet
              });
            }
          }
        }
      }

      handleCloseDialog();
      fetchData();
    } catch (error) {
      showAlert('Lỗi: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc muốn xóa môn học này?')) {
      try {
        await monHocAPI.delete(id);
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
    setTabValue(0);
  };

  const showAlert = (message, severity) => {
    setAlert({ open: true, message, severity });
  };

  const handleSoTietChange = (khoi, value) => {
    const newList = formData.khoi_list.map(item =>
      item.khoi === khoi ? { ...item, so_tiet: parseInt(value) || 0 } : item
    );
    setFormData({ ...formData, khoi_list: newList });
  };

  const handlePhanMonChange = (index, field, value) => {
    const newList = [...formData.phan_mon_list];
    newList[index][field] = value;
    setFormData({ ...formData, phan_mon_list: newList });
  };

  const addPhanMon = () => {
    const newPhanMon = {
      id: Date.now(),
      ma_phan_mon: '',
      ten_phan_mon: '',
      thu_tu: (formData.phan_mon_list?.length || 0) + 1,
      active: true
    };
    setFormData({
      ...formData,
      phan_mon_list: [...(formData.phan_mon_list || []), newPhanMon]
    });
  };

  const removePhanMon = (index) => {
    const newList = formData.phan_mon_list.filter((_, i) => i !== index);
    setFormData({ ...formData, phan_mon_list: newList });
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
          Thêm môn học
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
              <TableCell>Mã môn</TableCell>
              <TableCell>Tên môn</TableCell>
              <TableCell>Phân môn</TableCell>
              <TableCell>Số tiết theo khối</TableCell>
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
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">{item.ma_mon}</Typography>
                  </TableCell>
                  <TableCell>{item.ten_mon}</TableCell>
                  <TableCell>
                    {item.co_phan_mon && item.phan_mon_list && item.phan_mon_list.length > 0 ? (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {item.phan_mon_list.map(pm => (
                          <Chip
                            key={pm.id || pm.ma_phan_mon}
                            label={pm.ten_phan_mon}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="caption" color="textSecondary">
                        {item.co_phan_mon ? 'Chưa có phân môn' : 'Không có phân môn'}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {item.khoi_list && item.khoi_list.length > 0 ? (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxWidth: 200 }}>
                        {item.khoi_list.map(k => (
                          <Chip
                            key={k.id || k.khoi}
                            label={`K${k.khoi}: ${k.so_tiet}t`}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '11px' }}
                          />
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="caption" color="textSecondary">Chưa cấu hình</Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={item.active ? 'Hoạt động' : 'Vô hiệu'}
                      color={item.active ? 'success' : 'error'}
                      size="small"
                    />
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

      {/* Dialog thêm/sửa */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingItem ? '✏️ Chỉnh sửa môn học' : '➕ Thêm môn học mới'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
              <Tab label="Thông tin chính" />
              <Tab label="Phân môn" disabled={!formData.co_phan_mon} />
              <Tab label="Số tiết theo khối" />
            </Tabs>
          </Box>

          {/* Tab 1: Thông tin chính */}
          {tabValue === 0 && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Mã môn học"
                    value={formData.ma_mon}
                    onChange={(e) => setFormData({ ...formData, ma_mon: e.target.value })}
                    margin="dense"
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Tên môn học"
                    value={formData.ten_mon}
                    onChange={(e) => setFormData({ ...formData, ten_mon: e.target.value })}
                    margin="dense"
                    required
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <FormControl fullWidth margin="dense">
                    <InputLabel>Tổ chuyên môn</InputLabel>
                    <Select
                      value={formData.to_id || ''}
                      onChange={(e) => setFormData({ ...formData, to_id: e.target.value })}
                      label="Tổ chuyên môn"
                    >
                      <MenuItem value="">-- Không chọn --</MenuItem>
                      {toList.map((to) => (
                        <MenuItem key={to.id} value={to.id}>{to.ten_to}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Thứ tự"
                    type="number"
                    value={formData.thu_tu}
                    onChange={(e) => setFormData({ ...formData, thu_tu: parseInt(e.target.value) || 0 })}
                    margin="dense"
                  />
                </Grid>
              </Grid>

              <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.co_phan_mon}
                      onChange={(e) => setFormData({ ...formData, co_phan_mon: e.target.checked })}
                    />
                  }
                  label="Có phân môn"
                />
                <Button
                  variant={formData.active ? 'contained' : 'outlined'}
                  color={formData.active ? 'success' : 'default'}
                  onClick={() => setFormData({ ...formData, active: !formData.active })}
                >
                  {formData.active ? '✅ Hoạt động' : '❌ Không hoạt động'}
                </Button>
              </Box>
            </Box>
          )}

          {/* Tab 2: Phân môn */}
          {tabValue === 1 && formData.co_phan_mon && (
            <Box sx={{ mt: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Quản lý các phân môn của môn học này
                </Typography>
                <Button size="small" startIcon={<AddCircle />} onClick={addPhanMon}>
                  Thêm phân môn
                </Button>
              </Box>
              {formData.phan_mon_list?.length === 0 ? (
                <Typography variant="body2" color="textSecondary" align="center" sx={{ py: 2 }}>
                  Chưa có phân môn nào. Nhấn "Thêm phân môn" để tạo.
                </Typography>
              ) : (
                formData.phan_mon_list.map((pm, index) => (
                  <Box key={pm.id || index} sx={{ display: 'flex', gap: 1, mt: 1, alignItems: 'center' }}>
                    <TextField
                      size="small"
                      label="Mã"
                      value={pm.ma_phan_mon}
                      onChange={(e) => handlePhanMonChange(index, 'ma_phan_mon', e.target.value)}
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      size="small"
                      label="Tên phân môn"
                      value={pm.ten_phan_mon}
                      onChange={(e) => handlePhanMonChange(index, 'ten_phan_mon', e.target.value)}
                      sx={{ flex: 2 }}
                    />
                    <TextField
                      size="small"
                      label="Thứ tự"
                      type="number"
                      value={pm.thu_tu}
                      onChange={(e) => handlePhanMonChange(index, 'thu_tu', parseInt(e.target.value) || 0)}
                      sx={{ width: 80 }}
                    />
                    <IconButton size="small" color="error" onClick={() => removePhanMon(index)}>
                      <RemoveCircle />
                    </IconButton>
                  </Box>
                ))
              )}
            </Box>
          )}

          {/* Tab 3: Số tiết theo khối */}
          {tabValue === 2 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Cấu hình số tiết cho từng khối
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 2, mt: 1 }}>
                {KHOI_LIST.map(khoi => {
                  const item = formData.khoi_list?.find(k => k.khoi === khoi) || { khoi, so_tiet: 0 };
                  return (
                    <Box key={khoi} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ minWidth: 50 }}>
                        K{khoi}:
                      </Typography>
                      <TextField
                        size="small"
                        type="number"
                        value={item.so_tiet}
                        onChange={(e) => handleSoTietChange(khoi, e.target.value)}
                        sx={{ width: 70 }}
                        inputProps={{ min: 0, max: 10 }}
                      />
                      <Typography variant="caption">tiết</Typography>
                    </Box>
                  );
                })}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Hủy</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingItem ? 'Cập nhật' : 'Thêm mới'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={alert.open}
        autoHideDuration={3000}
        onClose={() => setAlert({ ...alert, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert severity={alert.severity}>{alert.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default MonHocTab;