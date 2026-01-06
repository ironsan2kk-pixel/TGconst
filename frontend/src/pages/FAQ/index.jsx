import { useState, useEffect } from 'react';
import { 
  HelpCircle, 
  Plus, 
  Edit, 
  Trash2,
  Search,
  ChevronDown,
  ChevronRight,
  MessageCircle
} from 'lucide-react';
import { Modal, ConfirmDialog } from '../../components';
// import { faqAPI, menuAPI } from '../../api/client';

export default function FAQ() {
  const [faqItems, setFaqItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState({});

  const [formData, setFormData] = useState({
    question_ru: '',
    question_en: '',
    answer_ru: '',
    answer_en: '',
    category_id: '',
    sort_order: 0,
    is_active: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // const [faqRes, menuRes] = await Promise.all([
      //   faqAPI.getAll(),
      //   menuAPI.getAll()
      // ]);
      // setFaqItems(faqRes.data);
      // Filter menu items to get only sections for categories
      // setCategories(menuRes.data.filter(item => item.type === 'section'));
      
      // Mock data
      setCategories([
        { id: 4, text_ru: 'FAQ', text_en: 'FAQ', icon: '❓' },
        { id: 7, text_ru: 'Обучение', text_en: 'Learning', icon: '📚' }
      ]);
      
      setFaqItems([
        {
          id: 1,
          question_ru: 'Как оплатить подписку?',
          question_en: 'How to pay for subscription?',
          answer_ru: 'Вы можете оплатить подписку криптовалютой USDT через CryptoBot. Выберите тариф, нажмите "Оплатить" и следуйте инструкциям.',
          answer_en: 'You can pay for subscription with USDT cryptocurrency via CryptoBot. Select a tariff, click "Pay" and follow the instructions.',
          category_id: 4,
          sort_order: 1,
          is_active: true,
          created_at: '2025-01-01T10:00:00Z'
        },
        {
          id: 2,
          question_ru: 'Как отменить подписку?',
          question_en: 'How to cancel subscription?',
          answer_ru: 'Подписка автоматически заканчивается по истечении оплаченного периода. Если нужна помощь, обратитесь в поддержку.',
          answer_en: 'Subscription automatically ends after the paid period expires. If you need help, contact support.',
          category_id: 4,
          sort_order: 2,
          is_active: true,
          created_at: '2025-01-01T10:00:00Z'
        },
        {
          id: 3,
          question_ru: 'Что такое промокод?',
          question_en: 'What is a promo code?',
          answer_ru: 'Промокод даёт скидку на покупку подписки. Введите его в разделе "Промокод" перед оплатой.',
          answer_en: 'A promo code gives you a discount on subscription purchase. Enter it in the "Promo Code" section before payment.',
          category_id: 4,
          sort_order: 3,
          is_active: true,
          created_at: '2025-01-01T10:00:00Z'
        },
        {
          id: 4,
          question_ru: 'Как получить доступ к каналам?',
          question_en: 'How to get channel access?',
          answer_ru: 'После успешной оплаты вы автоматически получите приглашения во все каналы, входящие в ваш тариф.',
          answer_en: 'After successful payment, you will automatically receive invitations to all channels included in your tariff.',
          category_id: 4,
          sort_order: 4,
          is_active: true,
          created_at: '2025-01-02T10:00:00Z'
        },
        {
          id: 5,
          question_ru: 'Где найти обучающие материалы?',
          question_en: 'Where to find learning materials?',
          answer_ru: 'Все обучающие материалы доступны в разделе "Обучение" главного меню. Там вы найдёте гайды и видео-уроки.',
          answer_en: 'All learning materials are available in the "Learning" section of the main menu. You will find guides and video tutorials there.',
          category_id: 7,
          sort_order: 1,
          is_active: true,
          created_at: '2025-01-03T10:00:00Z'
        }
      ]);

      // Expand all categories by default
      setExpandedCategories({ 4: true, 7: true });
    } catch (error) {
      console.error('Error fetching FAQ data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      if (selectedItem) {
        // await faqAPI.update(selectedItem.id, formData);
        console.log('Updating FAQ:', selectedItem.id, formData);
        setFaqItems(faqItems.map(item => 
          item.id === selectedItem.id ? { ...item, ...formData } : item
        ));
      } else {
        // const response = await faqAPI.create(formData);
        console.log('Creating FAQ:', formData);
        setFaqItems([...faqItems, { 
          id: Date.now(), 
          ...formData,
          created_at: new Date().toISOString()
        }]);
      }
      handleCloseModal();
    } catch (error) {
      console.error('Error saving FAQ:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;
    try {
      // await faqAPI.delete(selectedItem.id);
      console.log('Deleting FAQ:', selectedItem.id);
      setFaqItems(faqItems.filter(item => item.id !== selectedItem.id));
      setShowConfirm(false);
      setSelectedItem(null);
    } catch (error) {
      console.error('Error deleting FAQ:', error);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedItem(null);
    setFormData({
      question_ru: '',
      question_en: '',
      answer_ru: '',
      answer_en: '',
      category_id: '',
      sort_order: 0,
      is_active: true
    });
  };

  const openEditModal = (item) => {
    setSelectedItem(item);
    setFormData({
      question_ru: item.question_ru,
      question_en: item.question_en,
      answer_ru: item.answer_ru,
      answer_en: item.answer_en,
      category_id: item.category_id || '',
      sort_order: item.sort_order,
      is_active: item.is_active
    });
    setShowModal(true);
  };

  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.text_ru : 'Без категории';
  };

  const filteredItems = faqItems.filter(item => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      item.question_ru.toLowerCase().includes(query) ||
      item.question_en.toLowerCase().includes(query) ||
      item.answer_ru.toLowerCase().includes(query) ||
      item.answer_en.toLowerCase().includes(query)
    );
  });

  // Group items by category
  const groupedItems = {};
  filteredItems.forEach(item => {
    const catId = item.category_id || 'uncategorized';
    if (!groupedItems[catId]) {
      groupedItems[catId] = [];
    }
    groupedItems[catId].push(item);
  });

  // Sort items within each category
  Object.keys(groupedItems).forEach(catId => {
    groupedItems[catId].sort((a, b) => a.sort_order - b.sort_order);
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            FAQ
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Вопросы и ответы для пользователей
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Добавить вопрос
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <HelpCircle className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Всего вопросов</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {faqItems.length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <MessageCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Активных</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {faqItems.filter(f => f.is_active).length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Search className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Категорий</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {categories.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск по вопросам и ответам..."
            className="input pl-10"
          />
        </div>
      </div>

      {/* FAQ List by Category */}
      {loading ? (
        <div className="card p-8 text-center text-gray-500">
          Загрузка...
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">
          {searchQuery ? 'Ничего не найдено' : 'Нет вопросов. Добавьте первый!'}
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map(category => {
            const items = groupedItems[category.id] || [];
            if (items.length === 0 && searchQuery) return null;
            
            return (
              <div key={category.id} className="card overflow-hidden">
                <button
                  onClick={() => toggleCategory(category.id)}
                  className="w-full p-4 flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{category.icon}</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {category.text_ru}
                    </span>
                    <span className="text-sm text-gray-500">
                      ({items.length})
                    </span>
                  </div>
                  {expandedCategories[category.id] ? (
                    <ChevronDown className="w-5 h-5 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-500" />
                  )}
                </button>
                
                {expandedCategories[category.id] && items.length > 0 && (
                  <div className="divide-y divide-gray-200 dark:divide-gray-700">
                    {items.map(item => (
                      <div 
                        key={item.id}
                        className={`p-4 ${!item.is_active ? 'opacity-50' : ''}`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-gray-900 dark:text-white">
                              {item.question_ru}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                              {item.question_en}
                            </p>
                            <p className="text-gray-600 dark:text-gray-400 mt-2 text-sm">
                              {item.answer_ru}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {!item.is_active && (
                              <span className="badge-yellow text-xs">Скрыт</span>
                            )}
                            <button
                              onClick={() => openEditModal(item)}
                              className="p-1 text-gray-500 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedItem(item);
                                setShowConfirm(true);
                              }}
                              className="p-1 text-gray-500 hover:text-red-600 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {/* Uncategorized */}
          {groupedItems['uncategorized'] && groupedItems['uncategorized'].length > 0 && (
            <div className="card overflow-hidden">
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50">
                <span className="font-medium text-gray-900 dark:text-white">
                  Без категории ({groupedItems['uncategorized'].length})
                </span>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {groupedItems['uncategorized'].map(item => (
                  <div key={item.id} className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {item.question_ru}
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400 mt-2 text-sm">
                          {item.answer_ru}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openEditModal(item)}
                          className="p-1 text-gray-500 hover:text-primary-600"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedItem(item);
                            setShowConfirm(true);
                          }}
                          className="p-1 text-gray-500 hover:text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title={selectedItem ? 'Редактировать вопрос' : 'Добавить вопрос'}
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Вопрос (RU) *</label>
              <input
                type="text"
                value={formData.question_ru}
                onChange={(e) => setFormData({ ...formData, question_ru: e.target.value })}
                className="input"
                placeholder="Как оплатить?"
                required
              />
            </div>
            <div>
              <label className="label">Вопрос (EN) *</label>
              <input
                type="text"
                value={formData.question_en}
                onChange={(e) => setFormData({ ...formData, question_en: e.target.value })}
                className="input"
                placeholder="How to pay?"
                required
              />
            </div>
          </div>

          <div>
            <label className="label">Ответ (RU) *</label>
            <textarea
              value={formData.answer_ru}
              onChange={(e) => setFormData({ ...formData, answer_ru: e.target.value })}
              className="input min-h-[100px]"
              placeholder="Подробный ответ на русском..."
              required
            />
          </div>

          <div>
            <label className="label">Ответ (EN) *</label>
            <textarea
              value={formData.answer_en}
              onChange={(e) => setFormData({ ...formData, answer_en: e.target.value })}
              className="input min-h-[100px]"
              placeholder="Detailed answer in English..."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Категория</label>
              <select
                value={formData.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: e.target.value ? parseInt(e.target.value) : '' })}
                className="input"
              >
                <option value="">Без категории</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.icon} {cat.text_ru}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Порядок сортировки</label>
              <input
                type="number"
                value={formData.sort_order}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
                className="input"
                min="0"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300"
            />
            <label htmlFor="is_active" className="text-sm text-gray-700 dark:text-gray-300">
              Активен (показывать в боте)
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button onClick={handleCloseModal} className="btn-secondary">
              Отмена
            </button>
            <button
              onClick={handleSubmit}
              className="btn-primary"
              disabled={!formData.question_ru || !formData.question_en || !formData.answer_ru || !formData.answer_en}
            >
              {selectedItem ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Confirm Delete */}
      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => {
          setShowConfirm(false);
          setSelectedItem(null);
        }}
        onConfirm={handleDelete}
        title="Удалить вопрос?"
        message="Вопрос будет удалён из FAQ."
        confirmText="Удалить"
        type="danger"
      />
    </div>
  );
}
