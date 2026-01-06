import { useState, useEffect } from 'react'
import { Plus, Save, Trash2, GripVertical } from 'lucide-react'
import { Modal, ConfirmDialog, DragDropTree, MenuItemForm, MenuPreview } from '../../components'
import { menuAPI } from '../../api/client'

export default function MenuBuilder() {
  const [menuItems, setMenuItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [parentId, setParentId] = useState(null)

  useEffect(() => {
    loadMenu()
  }, [])

  const loadMenu = async () => {
    setLoading(true)
    try {
      const response = await menuAPI.getAll()
      const data = response.data.items || response.data; setMenuItems(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading menu:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (data) => {
    try {
      if (selectedItem) {
        await menuAPI.update(selectedItem.id, data)
      } else {
        await menuAPI.create({ ...data, parent_id: parentId })
      }
      setIsModalOpen(false)
      setSelectedItem(null)
      setParentId(null)
      loadMenu()
    } catch (error) {
      console.error('Error saving menu item:', error)
    }
  }

  const handleDelete = async () => {
    try {
      await menuAPI.delete(selectedItem.id)
      setIsDeleteOpen(false)
      setSelectedItem(null)
      loadMenu()
    } catch (error) {
      console.error('Error deleting menu item:', error)
    }
  }

  const handleReorder = async (items) => {
    try {
      await menuAPI.reorder(items.map((item, index) => ({
        id: item.id,
        sort_order: index,
        parent_id: item.parent_id
      })))
      setMenuItems(items)
    } catch (error) {
      console.error('Error reordering:', error)
    }
  }

  const openAddModal = (parentItemId = null) => {
    setSelectedItem(null)
    setParentId(parentItemId)
    setIsModalOpen(true)
  }

  const openEditModal = (item) => {
    setSelectedItem(item)
    setParentId(item.parent_id)
    setIsModalOpen(true)
  }

  const openDeleteDialog = (item) => {
    setSelectedItem(item)
    setIsDeleteOpen(true)
  }

  // Build tree structure
  const buildTree = (items, parentId = null) => {
    return items
      .filter(item => item.parent_id === parentId)
      .sort((a, b) => a.sort_order - b.sort_order)
      .map(item => ({
        ...item,
        children: buildTree(items, item.id)
      }))
  }

  const treeData = buildTree(menuItems)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Конструктор меню</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Настройка главного меню бота
          </p>
        </div>
        <button onClick={() => openAddModal()} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Добавить пункт
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Menu Tree */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Структура меню</h3>
          {treeData.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Меню пустое. Добавьте первый пункт.
            </p>
          ) : (
            <DragDropTree
              items={treeData}
              onReorder={handleReorder}
              onEdit={openEditModal}
              onDelete={openDeleteDialog}
              onAdd={openAddModal}
            />
          )}
        </div>

        {/* Preview */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Превью</h3>
          <MenuPreview items={treeData} />
        </div>
      </div>

      {/* Add/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedItem(null)
          setParentId(null)
        }}
        title={selectedItem ? 'Редактировать пункт' : 'Добавить пункт'}
        size="lg"
      >
        <MenuItemForm
          initialData={selectedItem}
          onSubmit={handleSave}
          onCancel={() => {
            setIsModalOpen(false)
            setSelectedItem(null)
            setParentId(null)
          }}
        />
      </Modal>

      {/* Delete Confirm */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить пункт меню"
        message={`Удалить "${selectedItem?.text_ru}"? Все вложенные пункты также будут удалены.`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
