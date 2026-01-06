import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area,
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend 
} from 'recharts'
import { useTheme } from '../context/ThemeContext'

export default function Chart({ 
  data, 
  type = 'line', 
  dataKey = 'value',
  xAxisKey = 'date',
  title,
  color = '#3b82f6',
  height = 300,
  showGrid = true,
  showLegend = false
}) {
  const { darkMode } = useTheme()
  
  const axisColor = darkMode ? '#6b7280' : '#9ca3af'
  const gridColor = darkMode ? '#374151' : '#e5e7eb'
  const tooltipBg = darkMode ? '#1f2937' : '#ffffff'
  const tooltipBorder = darkMode ? '#374151' : '#e5e7eb'

  const commonProps = {
    data,
    margin: { top: 10, right: 10, left: 0, bottom: 0 }
  }

  const renderChart = () => {
    switch (type) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />}
            <XAxis dataKey={xAxisKey} tick={{ fill: axisColor, fontSize: 12 }} />
            <YAxis tick={{ fill: axisColor, fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: tooltipBg, 
                border: `1px solid ${tooltipBorder}`,
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }} 
            />
            {showLegend && <Legend />}
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              fill={color} 
              fillOpacity={0.2}
            />
          </AreaChart>
        )
      
      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />}
            <XAxis dataKey={xAxisKey} tick={{ fill: axisColor, fontSize: 12 }} />
            <YAxis tick={{ fill: axisColor, fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: tooltipBg, 
                border: `1px solid ${tooltipBorder}`,
                borderRadius: '8px'
              }} 
            />
            {showLegend && <Legend />}
            <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
          </BarChart>
        )
      
      default:
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />}
            <XAxis dataKey={xAxisKey} tick={{ fill: axisColor, fontSize: 12 }} />
            <YAxis tick={{ fill: axisColor, fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: tooltipBg, 
                border: `1px solid ${tooltipBorder}`,
                borderRadius: '8px'
              }} 
            />
            {showLegend && <Legend />}
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              dot={{ fill: color, strokeWidth: 2 }}
            />
          </LineChart>
        )
    }
  }

  return (
    <div className="card p-6">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  )
}
