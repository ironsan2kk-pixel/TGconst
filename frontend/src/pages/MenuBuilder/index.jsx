import { useState, useEffect } from 'react';
import { 
  Plus, 
  Save,
  Eye,
  Trash2,
  Edit,
  FolderOpen,
  Link,
  MessageSquare,
  HelpCircle,
  Settings,
  GripVertical,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import { Modal, ConfirmDialog, DragDropTree, MenuItemForm, MenuPreview } from '../../components';
// import { menuAPI } from '../../api/client';

export default function MenuBuilder() {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [parentId, setParentId] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchMenuItems();
  }, []);

  const fetchMenuItems = async () => {
    setLoading(true);
    try {
      // const response = await menuAPI.getAll();
      // setMenuItems(buildTree(response.data));
      
      // Mock data - flat list that will be converted to tree
      const mockData = [
        {
          id: 1,
          parent_id: null,
          type: 'system',
          system_action: 'tariffs',
          text_ru: 'Тарифы',
          text_en: 'Pricing',
          icon: '📺',
          value: null,
          visibility: 'not_subscribed',
          visibility_language: 'all',
          sort_order: 1,
          is_active: true
        },
        {
          id: 2,
          parent_id: null,
          type: 'system',
          system_action: 'subscriptions',
          text_ru: 'Мои подписки',
          text_en: 'My Subscriptions',
          icon: '💳',
          value: null,
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 2,
          is_active: true
        },
        {
          id: 3,
          parent_id: null,
          type: 'system',
          system_action: 'promocode',
          text_ru: 'Промокод',
          text_en: 'Promo Code',
          icon: '🎁',
          value: null,
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 3,
          is_active: true
        },
        {
          id: 4,
          parent_id: null,
          type: 'section',
          system_action: null,
          text_ru: 'FAQ',
          text_en: 'FAQ',
          icon: '❓',
          value: null,
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 4,
          is_active: true
        },
        {
          id: 5,
          parent_id: 4,
          type: 'faq',
          system_action: null,
          text_ru: 'Как оплатить?',
          text_en: 'How to pay?',
          icon: '💰',
          value: '1', // faq_id
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 1,
          is_active: true
        },
        {
          id: 6,
          parent_id: 4,
          type: 'faq',
          system_action: null,
          text_ru: 'Как отменить подписку?',
          text_en: 'How to cancel?',
          icon: '❌',
          value: '2',
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 2,
          is_active: true
        },
        {
          id: 7,
          parent_id: null,
          type: 'section',
          system_action: null,
          text_ru: 'Обучение',
          text_en: 'Learning',
          icon: '📚',
          value: null,
          visibility: 'subscribed',
          visibility_language: 'all',
          sort_order: 5,
          is_active: true
        },
        {
          id: 8,
          parent_id: 7,
          type: 'text',
          system_action: null,
          text_ru: 'Гайд для новичков',
          text_en: 'Beginner Guide',
          icon: '📖',
          value: 'Добро пожаловать! Вот ваш гайд для начала работы...',
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 1,
          is_active: true
        },
        {
          id: 9,
          parent_id: 7,
          type: 'link',
          system_action: null,
          text_ru: 'Видео-уроки',
          text_en: 'Video Tutorials',
          icon: '🎥',
          value: 'https://youtube.com/playlist',
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 2,
          is_active: true
        },
        {
          id: 10,
          parent_id: null,
          type: 'link',
          system_action: null,
          text_ru: 'Наш канал',
          text_en: 'Our Channel',
          icon: '📢',
          value: 'https://t.me/channel',
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 6,
          is_active: true
        },
        {
          id: 11,
          parent_id: null,
          type: 'system',
          system_action: 'language',
          text_ru: 'Язык',
          text_en: 'Language',
          icon: '🌐',
          value: null,
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 7,
          is_active: true
        },
        {
          id: 12,
          parent_id: null,
          type: 'system',
          system_action: 'support',
          text_ru: 'Поддержка',
          text_en: 'Support',
          icon: '💬',
          value: null,
          visibility: 'all',
          visibility_language: 'all',
          sort_order: 8,
          is_active: true
        }
      ];

      setMenuItems(buildTree(mockData));
    } catch (error) {
      console.error('Error fetching menu items:', error);
    } finally {
      setLoading(false);
    }
  };

  // Convert flat list to tree structure
  const buildTree = (items) => {
    const map = {};
    const roots = [];

    items.forEach(item => {
      map[item.id] = { ...item, children: [] };
    });

    items.forEach(item => {
      if (item.parent_id === null) {
        roots.push(map[item.id]);
      } else if (map[item.parent_id]) {
        map[item.parent_id].children.push(map[item.id]);
      }
    });

    // Sort by sort_order
    const sortChildren = (nodes) => {
      nodes.sort((a, b) => a.sort_order - b.sort_order);
      nodes.forEach(node => {
        if (node.children.length > 0) {
          sortChildren(node.children);
        }
      });
    };
    sortChildren(roots);

    return roots;
  };

  // Flatten tree back to list
  const flattenTree = (items, parentId = null) => {
    let result = [];
    items.forEach((item, index) => {
      result.push({
        ...item,
        parent_id: parentId,
        sort_order: index + 1,
        children: undefined
      });
      if (item.children && item.children.length > 0) {
        result = result.concat(flattenTree(item.children, item.id));
      }
    });
    return result;
  };

  const handleSave = async () => {
    try {
      const flatItems = flattenTree(menuItems);
      // await menuAPI.updateAll(flatItems);
      console.log('Saving menu items:', flatItems);
      setHasChanges(false);
    } catch (error) {
      console.error('Error saving menu:', error);
    }
  };

  const handleAdd = async (formData) => {
    try {
      // const response = await menuAPI.create({ ...formData, parent_id: parentId });
      console.log('Adding menu item:', { ...formData, parent_id: parentId });
      
      // Mock: add to local state
      const newItem = {
        id: Date.now(),
        ...formData,
        parent_id: parentId,
        children: []
      };
      
      if (parentId === null) {
        setMenuItems([...menuItems, newItem]);
      } else {
        // Add to parent's children
        const addToParent = (items) => {
          return items.map(item => {
            if (item.id === parentId) {
              return { ...item, children: [...item.children, newItem] };
            }
            if (item.children.length > 0) {
              return { ...item, children: addToParent(item.children) };
            }
            return item;
          });
        };
        setMenuItems(addToParent(menuItems));
      }
      
      setShowAddModal(false);
      setParentId(null);
      setHasChanges(true);
    } catch (error) {
      console.error('Error adding menu item:', error);
    }
  };

  const handleEdit = async (formData) => {
    try {
      // await menuAPI.update(selectedItem.id, formData);
      console.log('Updating menu item:', selectedItem.id, formData);
      
      // Mock: update in local state
      const updateItem = (items) => {
        return items.map(item => {
          if (item.id === selectedItem.id) {
            return { ...item, ...formData };
          }
          if (item.children.length > 0) {
            return { ...item, children: updateItem(item.children) };
          }
          return item;
        });
      };
      setMenuItems(updateItem(menuItems));
      
      setShowEditModal(false);
      setSelectedItem(null);
      setHasChanges(true);
    } catch (error) {
      console.error('Error updating menu item:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;
    try {
      // await menuAPI.delete(selectedItem.id);
      console.log('Deleting menu item:', selectedItem.id);
      
      // Mock: remove from local state
      const removeItem = (items) => {
        return items
          .filter(item => item.id !== selectedItem.id)
          .map(item => ({
            ...item,
            children: removeItem(item.children)
          }));
      };
      setMenuItems(removeItem(menuItems));
      
      setShowConfirm(false);
      setSelectedItem(null);
      setHasChanges(true);
    } catch (error) {
      console.error('Error deleting menu item:', error);
    }
  };

  const handleReorder = (newItems) => {
    setMenuItems(newItems);
    setHasChanges(true);
  };

  const getTypeIcon = (type) => {
    const icons = {
      section: FolderOpen,
      link: Link,
      text: MessageSquare,
      faq: HelpCircle,
      system: Settings
    };
    return icons[type] || Settings;
  };

  const getTypeLabel = (type) => {
    const labels = {
      section: 'Раздел',
      link: 'Ссылка',
      text: 'Текст',
      faq: 'FAQ',
      system: 'Системный'
    };
    return labels[type] || type;
  };

  const getVisibilityLabel = (visibility) => {
    const labels = {
      all: 'Все',
      subscribed: 'С подпиской',
      not_subscribed: 'Без подписки'
    };
    return labels[visibility] || visibility;
  };

  // Recursive tree item component
  const TreeItem = ({ item, level = 0 }) => {
    const [expanded, setExpanded] = useState(true);
    const hasChildren = item.children && item.children.length > 0;
    const TypeIcon = getTypeIcon(item.type);

    return (
      <div className="select-none">
        <div 
          className={`
            flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
            ${!item.is_active ? 'opacity-50' : ''}
          `}
          style={{ paddingLeft: `${level * 24 + 8}px` }}
        >
          <GripVertical className="w-4 h-4 text-gray-400 cursor-grab" />
          
          {hasChildren ? (
            <button 
              onClick={() => setExpanded(!expanded)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
            >
              {expanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          ) : (
            <div className="w-6" />
          )}

          <span className="text-xl">{item.icon}</span>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900 dark:text-white truncate">
                {item.text_ru}
              </span>
              <span className="text-xs text-gray-500">
                ({item.text_en})
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <TypeIcon className="w-3 h-3" />
              <span>{getTypeLabel(item.type)}</span>
              {item.visibility !== 'all' && (
                <>
                  <span>•</span>
                  <span>{getVisibilityLabel(item.visibility)}</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1">
            {item.type === 'section' && (
              <button
                onClick={() => {
                  setParentId(item.id);
                  setShowAddModal(true);
                }}
                className="p-1 text-gray-500 hover:text-primary-600 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                title="Добавить в раздел"
              >
                <Plus className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => {
                setSelectedItem(item);
                setShowEditModal(true);
              }}
              className="p-1 text-gray-500 hover:text-primary-600 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title="Редактировать"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setSelectedItem(item);
                setShowConfirm(true);
              }}
              className="p-1 text-gray-500 hover:text-red-600 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title="Удалить"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {hasChildren && expanded && (
          <div>
            {item.children.map(child => (
              <TreeItem key={child.id} item={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Конструктор меню
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Настройка главного меню бота
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowPreview(true)}
            className="btn-secondary flex items-center gap-2"
          >
            <Eye className="w-5 h-5" />
            Превью
          </button>
          <button
            onClick={() => {
              setParentId(null);
              setShowAddModal(true);
            }}
            className="btn-secondary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить
          </button>
          <button
            onClick={handleSave}
            className="btn-primary flex items-center gap-2"
            disabled={!hasChanges}
          >
            <Save className="w-5 h-5" />
            Сохранить
            {hasChanges && <span className="w-2 h-2 bg-white rounded-full" />}
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Типы элементов:</strong> Раздел (подменю), Ссылка (URL), Текст (сообщение), 
          FAQ (вопрос-ответ), Системный (тарифы, подписки, язык, поддержка).
          <br />
          <strong>Условия показа:</strong> Элементы можно показывать всем, только с подпиской 
          или только без подписки.
        </p>
      </div>

      {/* Menu Tree */}
      <div className="card">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-medium text-gray-900 dark:text-white">
            Структура меню
          </h2>
        </div>
        
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            Загрузка...
          </div>
        ) : menuItems.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            Меню пустое. Добавьте первый элемент.
          </div>
        ) : (
          <div className="p-4 space-y-1">
            {menuItems.map(item => (
              <TreeItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>

      {/* Add Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setParentId(null);
        }}
        title={parentId ? "Добавить в раздел" : "Добавить элемент"}
        size="lg"
      >
        <MenuItemForm
          onSubmit={handleAdd}
          onCancel={() => {
            setShowAddModal(false);
            setParentId(null);
          }}
          isSubItem={parentId !== null}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedItem(null);
        }}
        title="Редактировать элемент"
        size="lg"
      >
        {selectedItem && (
          <MenuItemForm
            initialData={selectedItem}
            onSubmit={handleEdit}
            onCancel={() => {
              setShowEditModal(false);
              setSelectedItem(null);
            }}
            isSubItem={selectedItem.parent_id !== null}
          />
        )}
      </Modal>

      {/* Preview Modal */}
      <Modal
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        title="Превью меню"
        size="sm"
      >
        <MenuPreview items={menuItems} />
      </Modal>

      {/* Confirm Delete */}
      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => {
          setShowConfirm(false);
          setSelectedItem(null);
        }}
        onConfirm={handleDelete}
        title="Удалить элемент?"
        message={
          selectedItem?.children?.length > 0
            ? "Элемент содержит вложенные пункты. Они тоже будут удалены."
            : "Элемент будет удалён из меню."
        }
        confirmText="Удалить"
        type="danger"
      />
    </div>
  );
}
