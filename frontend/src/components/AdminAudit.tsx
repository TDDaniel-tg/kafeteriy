import { useState } from "react";
import { ShieldCheck, ShieldAlert, Lock, CheckCircle2 } from "lucide-react";
import { Button, DataTable, Badge, Tabs, Drawer } from "../ui";

export function AdminAudit({ onToast }: { onToast: (msg: string) => void }) {
  const [tab, setTab] = useState("Финансовый аудит");
  const [selectedAnomaly, setSelectedAnomaly] = useState<any>(null);

  const [auditRows] = useState([
    { id: "1", date: "24.09.2025 14:20", actor: "Елена Михайлова", action: "Ручное начисление", target: "Анна Морозова", details: "+1 500 б. (2FA TOTP подтверждено)" },
    { id: "2", date: "24.09.2025 12:15", actor: "Анна Морозова", action: "Списание за заказ", target: "КЛ-24051", details: "-2 400 б. (Английский Skyeng)" },
    { id: "3", date: "24.09.2025 10:00", actor: "Система (Celery)", action: "Проверка сгорания", target: "Партия #812", details: "Уведомление за 30 дней (800 б.)" },
    { id: "4", date: "23.09.2025 17:40", actor: "Елена Михайлова", action: "Изменение настройки", target: "PlatformSetting", details: "Комиссия перевода: 25% (v.2)" },
    { id: "5", date: "22.09.2025 09:30", actor: "Дмитрий Козлов", action: "Вход в систему", target: "Сессия", details: "SSO вход (IP: 192.168.1.45)" },
  ]);

  const [anomalies, setAnomalies] = useState([
    { id: "АН-101", user: "Анна Морозова", rule: "Крупное списание", details: "Заказ свыше 5 000 б.", status: "Обнаружено" },
    { id: "АН-098", user: "Михаил Соколов", rule: "Частые переводы", details: "3 перевода за 1 час", status: "Легитимно" },
  ]);

  const handleResolveAnomaly = (action: "legitimate" | "block") => {
    if (!selectedAnomaly) return;
    setAnomalies(anomalies.map(a => a.id === selectedAnomaly.id ? { ...a, status: action === "block" ? "Аккаунт заблокирован" : "Легитимно" } : a));
    setSelectedAnomaly(null);
    onToast(action === "block" ? "Аккаунт сотрудника временно заблокирован" : "Операция подтверждена как легитимная");
  };

  return (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">БЕЗОПАСНОСТЬ</span>
          <h1>Журнал аудита и аномалии (АДМ-24)</h1>
          <p>Неизменяемый реестр операций с проверкой хеш-сигнатуры и контроль аномалий</p>
        </div>
      </div>

      <div className="surface-card">
        <Tabs items={["Финансовый аудит", "Журнал аномалий"]} value={tab} onChange={setTab} />
      </div>

      {tab === "Финансовый аудит" && (
        <div className="surface-card table-card">
          <DataTable
            rows={auditRows}
            columns={[
              { key: "date", label: "Время" },
              { key: "actor", label: "Пользователь / Источник" },
              { key: "action", label: "Действие" },
              { key: "target", label: "Объект" },
              { key: "details", label: "Детали операции", render: r => <strong>{r.details}</strong> },
            ]}
          />
        </div>
      )}

      {tab === "Журнал аномалий" && (
        <div className="surface-card table-card">
          <DataTable
            rows={anomalies}
            columns={[
              { key: "id", label: "Тикет аномалии" },
              { key: "user", label: "Сотрудник" },
              { key: "rule", label: "Сработавшее правило" },
              { key: "details", label: "Описание подозрения" },
              { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Обнаружено" ? "warning" : r.status === "Легитимно" ? "success" : "danger"}>{r.status}</Badge> },
            ]}
            onRow={r => setSelectedAnomaly(r)}
          />
        </div>
      )}

      {selectedAnomaly && (
        <Drawer
          title={`Аномалия ${selectedAnomaly.id}`}
          onClose={() => setSelectedAnomaly(null)}
          footer={
            <div className="flex gap-2 w-full">
              <Button variant="danger" className="w-1/2" onClick={() => handleResolveAnomaly("block")}>
                Заблокировать аккаунт
              </Button>
              <Button className="w-1/2" onClick={() => handleResolveAnomaly("legitimate")}>
                Отметить как легитимно
              </Button>
            </div>
          }
        >
          <div className="form-stack">
            <div className="summary-row">
              <span>Сотрудник</span>
              <strong>{selectedAnomaly.user}</strong>
            </div>
            <div className="summary-row">
              <span>Правило</span>
              <strong>{selectedAnomaly.rule}</strong>
            </div>
            <div className="summary-row">
              <span>Детали</span>
              <strong>{selectedAnomaly.details}</strong>
            </div>
            <p className="text-sm text-gray-500">
              Администратор может подтвердить операцию как штатную либо заблокировать аккаунт до выяснения обстоятельств (ФТ-АУД.3).
            </p>
          </div>
        </Drawer>
      )}
    </>
  );
}
