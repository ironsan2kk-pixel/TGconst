import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Send } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Alert } from '../../components/ui/Badge';
import { createBroadcast } from '../../api/broadcasts';

export default function BroadcastCreate() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    message_text: '',
    message_photo: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.message_text.trim()) {
      setError('Введите текст сообщения');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await createBroadcast(uuid, {
        message_text: formData.message_text.trim(),
        message_photo: formData.message_photo.trim() || null,
      });
      navigate(`/bots/${uuid}/broadcasts`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при создании рассылки');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to={`/bots/${uuid}/broadcasts`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Новая рассылка</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Создание рассылки</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Textarea
              label="Текст сообщения"
              placeholder="Введите текст рассылки..."
              rows={6}
              value={formData.message_text}
              onChange={(e) => setFormData({ ...formData, message_text: e.target.value })}
              required
            />

            <Input
              label="Фото (URL)"
              placeholder="https://example.com/image.jpg"
              value={formData.message_photo}
              onChange={(e) => setFormData({ ...formData, message_photo: e.target.value })}
            />

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Предпросмотр</h4>
              <div className="bg-white border rounded-lg p-4">
                {formData.message_photo && (
                  <img 
                    src={formData.message_photo} 
                    alt="Preview" 
                    className="max-w-xs rounded-lg mb-3"
                    onError={(e) => e.target.style.display = 'none'}
                  />
                )}
                <p className="text-gray-800 whitespace-pre-wrap">
                  {formData.message_text || 'Текст сообщения...'}
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                <Send className="w-4 h-4 mr-2" />
                Создать рассылку
              </Button>
              <Link to={`/bots/${uuid}/broadcasts`}>
                <Button type="button" variant="secondary">
                  Отмена
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="py-4">
          <p className="text-sm text-gray-600">
            <strong>Примечание:</strong> После создания рассылки она будет в статусе "Ожидает". 
            Вам нужно будет запустить её вручную. Рассылка будет отправлена всем пользователям бота.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
