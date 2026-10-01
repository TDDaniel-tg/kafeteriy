import { useState } from "react";
import { SlidersHorizontal, RefreshCw, CheckCircle2, AlertCircle, Wifi, Server } from "lucide-react";
import { Button, DataTable, Badge, Toast } from "../ui";

export function AdminIntegrations({ onToast }: { onToast: (msg: string) => void }) {
  const [channels, setChannels] = useState([
    { id: "1", name: "1С:ЗУП", type: "Реестр сотрудников", status: "Доступно", ping: "45 мс", mode: "Mock" },
    { id: "2", name: "Корпоративный SSO (OIDC/SAML)", type: "Аутентификация", status: "Доступно", ping: "28 мс", mode: "Mock" },
    { id: "3", name: "Почтовый шлюз SMTP", type: "Уведомления", status: "Доступно", ping: "120 мс", mode: "Mock" },
    { id: "4", name: "Giftery API", type: "Подарочные карты", status: "Доступно", ping: "60 мс", mode: "Mock" },
    { id: "5", name: "ПВК / Prostodar API", type: "Виртуальные карты", status: "Доступно", ping: "65 мс", mode: "Mock" },
    { id: "6", name: "Бухгалтерия (файловый канал)", type: "Экспорт ведомостей", status: "Доступно", ping: "15 мс", mode: "Mock" },
  ]);
  const [testing, setTesting] = useState(false);

  const testAll = () => {
    setTesting(true);
    setTimeout(() => {
      setTesting(false);
      onToast("Все 6 каналов проверены: соединение успешно установлено");
    }, 800);
  };

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ИНФРАСТРУКТУРА</span>
          <h1>Интеграции и каналы связи (АДМ-21)</h1>
          <p>Мониторинг состояния подключённых внешних систем и поставщиков услуг</p>
        </div>
        <Button variant="secondary" onClick={testAll} loading={testing}>
          <RefreshCw size={16} /> Проверить доступность каналов
        </Button>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>Статус системы <Wifi size={18} /></span>
          <strong>Все каналы активны</strong>
          <small>6 из 6 сервисов доступны</small>
        </div>
        <div className="kpi-card">
          <span>Режим интеграций <Server size={18} /></span>
          <strong>Mock / Standalone</strong>
          <small>Система готова к автономной работе</small>
        </div>
        <div className="kpi-card">
          <span>Среднее время ответа <CheckCircle2 size={18} /></span>
          <strong>48 мс</strong>
          <small>Задержка в пределах нормы (&lt; 500 мс)</small>
        </div>
      </div>

      <div className="surface-card table-card">
        <DataTable
          rows={channels}
          columns={[
            { key: "name", label: "Интеграция" },
            { key: "type", label: "Назначение" },
            { key: "ping", label: "Время ответа" },
            { key: "mode", label: "Режим работы", render: r => <Badge tone="info">{r.mode}</Badge> },
            { key: "status", label: "Доступность", render: r => <Badge tone={r.status === "Доступно" ? "success" : "danger"}>{r.status}</Badge> },
          ]}
          onRow={r => onToast(`Канал ${r.name}: проверен, отклик ${r.ping}`)}
        />
      </div>
    </>
  );
}
