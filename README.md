# 每日任务追踪器

## 介绍
**每日任务追踪器** 是一个简单直观的任务管理应用，基于 **Tkinter** 构建。它帮助用户管理每日任务，跟踪完成情况，并通过 **贡献式热力图** 可视化任务进度。
*本项目主要为个人使用，可能存在较多bug和错误

<p align="center">
  <img src="https://github.com/user-attachments/assets/7d45e799-8bc1-4d2b-be60-c15e1ebe0241" alt="每日任务追踪器界面" width="600">
</p>


## 功能特点
- ✅ **添加 & 删除任务**：轻松管理每日待办事项。
- ✅ **热力图可视化**：以图形方式展示任务完成度，一目了然。
- ✅ **年份切换**：支持查看不同年份的任务数据。

## 安装 & 使用
### 依赖环境
- 需要 **Python 3.x** 环境。

## 使用指南
1. **添加任务**
   - 点击 **➕ 添加任务** 并输入任务名称。
2. **标记任务完成**
   - 勾选任务旁的复选框，表示任务已完成。
3. **保存进度**
   - 点击 **💾 保存进度**，记录当天任务完成情况。
4. **删除任务**
   - 在下拉菜单中选择任务，点击 **🗑 删除任务** 进行移除。
5. **查看任务进度热力图**
   - 悬停在日期上可查看任务完成情况。
   - 使用下拉框切换不同年份的数据。
<p align="center">
  <img src="https://github.com/user-attachments/assets/f074104b-00d5-43e7-bf37-45b6620b4d21" alt="任务热力图示例" width="600">
</p>


## 数据存储方式
- **`tasks.json`** 存储：
  - `tasks`：任务列表。
  - `history`：每日任务完成情况。
- 每次修改任务或保存进度时，数据会自动更新。
