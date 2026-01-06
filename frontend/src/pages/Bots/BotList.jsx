import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Bot, Play, Square, RotateCw, Trash2, Settings } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge, Spinner, Modal, EmptyState } from '../../components/ui/Badge'
import botsApi from '../../api/bots'

export default function BotList() {
  const [bots, setBots] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)
  const [deleteModal, setDeleteModal] = useState(null)

  useEffect(() => {
    loadBots()
  }, [])

  const loadBots = async () => {
    try {
      const data = await botsApi.list()
      setBots(data)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (uuid) => {
    setActionLoading(uuid)
    try {
      await botsApi.start(uuid)
      await loadBots()
    } finally {
      setActionLoading(null)
    }
  }

  const handleStop = async (uuid) => {
    setActionLoading(uuid)
    try {
      await botsApi.stop(uuid)
      await loadBots()
    } finally {
      setActionLoading(null)
    }
  }

  const handleRestart = async (uuid) => {
    setActionLoading(uuid)
    try {
      await botsApi.restart(uuid)
      await loadBots()
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    setActionLoading(deleteModal)
    try {
      await botsApi.delete(deleteModal)
      await loadBots()
    } finally {
      setActionLoading(null)
      setDeleteModal(null)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Боты</h1>
        <Link to="/bots/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Создать бота
          </Button>
        </Link>
      </div>

      {bots.length === 0 ? (
        <Card>
          <CardContent>
            <EmptyState
              icon={Bot}
              title="Нет ботов"
              description="Создайте первого бота для начала работы"
              action={
                <Link to="/bots/create">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Создать бота
                  </Button>
                </Link>
              }
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {bots.map((bot) => (
            <Card key={bot.uuid}>
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Bot className="w-6 h-6 text-gray-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{bot.name}</h3>
                      <p className="text-sm text-gray-500">{bot.uuid}</p>
                    </div>
                    <Badge variant={bot.is_active ? 'success' : 'default'}>
                      {bot.is_active ? 'Активен' : 'Остановлен'}
                    </Badge>
                    {bot.process_pid && (
                      <span className="text-xs text-gray-400">PID: {bot.process_pid}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {bot.is_active ? (
                      <>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleStop(bot.uuid)}
                          loading={actionLoading === bot.uuid}
                        >
                          <Square className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleRestart(bot.uuid)}
                          loading={actionLoading === bot.uuid}
                        >
                          <RotateCw className="w-4 h-4" />
                        </Button>
                      </>
                    ) : (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleStart(bot.uuid)}
                        loading={actionLoading === bot.uuid}
                      >
                        <Play className="w-4 h-4" />
                      </Button>
                    )}
                    <Link to={`/bots/${bot.uuid}/edit`}>
                      <Button variant="ghost" size="sm">
                        <Settings className="w-4 h-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteModal(bot.uuid)}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Удаление бота"
      >
        <p className="text-gray-600 mb-6">
          Вы уверены? Это действие удалит бота и все его данные.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteModal(null)}>
            Отмена
          </Button>
          <Button variant="danger" onClick={handleDelete} loading={!!actionLoading}>
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  )
}
