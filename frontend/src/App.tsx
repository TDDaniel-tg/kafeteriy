import { useState, useEffect, type ReactNode } from "react";
import { Activity, ArrowDownRight, ArrowLeft, ArrowRight, ArrowUpRight, BarChart3, Bell, BookOpen, CalendarDays, Check, ChevronDown, ChevronRight, CircleHelp, ClipboardList, Clock3, CloudUpload, Coins, Download, FileCheck2, FileText, Gift, Heart, HeartPulse, Home, LayoutDashboard, LifeBuoy, LockKeyhole, Mail, Menu, MoreHorizontal, Package, Plus, Search, Settings, ShieldCheck, ShoppingBag, ShoppingCart, SlidersHorizontal, Sparkles, Ticket, Trash2, TrendingUp, Users, Wallet, X, AlertTriangle } from "lucide-react";
import { Alert, Avatar, Badge, BalancePill, Breadcrumbs, Button, Checkbox, DataTable, DateField, Drawer, EmptyState, Field, FileUploader, IconButton, LinkButton, Modal, points, Progress, SearchField, Select, Skeleton, Slider, Stepper, Tabs, Toast, Toggle } from "./ui";
import DeveloperCredit from "./DeveloperCredit";
import { AdminWindows } from "./components/AdminWindows";
import { AdminComms } from "./components/AdminComms";
import { AdminSurveys } from "./components/AdminSurveys";
import { AdminIntegrations } from "./components/AdminIntegrations";
import { AdminReports } from "./components/AdminReports";
import { AdminSupport } from "./components/AdminSupport";
import { AdminAudit } from "./components/AdminAudit";
import { api, type ProductItem, type OrderRow, type UserProfile } from "./api";

type Product = { id: string; name: string; category: string; supplier: string; price: number; image: string; tag?: string; type: string; description: string; available?: boolean; is_general_offer?: boolean };

const initialProducts: Product[] = [
  { id: "english", name: "Английский для жизни и работы", category: "Обучение", supplier: "Skyeng", price: 2400, image: "https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=700&q=80", tag: "Популярное", type: "Обучение", description: "Индивидуальные занятия с преподавателем в удобное время. Учитесь в своём темпе и уверенно говорите на английском.", is_general_offer: true },
  { id: "retreat", name: "Выходные на базе отдыха", category: "Отдых", supplier: "Лес и озеро", price: 3200, image: "https://images.unsplash.com/photo-1619688137428-851529e61a0f?w=700&q=80", tag: "Новинка", type: "Проживание", description: "Два дня вдали от городской суеты: уютный домик у озера, прогулки по лесу и время для себя.", is_general_offer: true },
  { id: "gift", name: "Подарочная карта Giftery", category: "Подарки", supplier: "Giftery", price: 1500, image: "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=700&q=80", tag: "Хит", type: "Сертификат", description: "Один сертификат — сотни любимых магазинов. Порадуйте себя или близких подарком на выбор.", is_general_offer: true },
  { id: "psych", name: "Консультация психолога", category: "Здоровье", supplier: "Ясно", price: 1800, image: "https://images.unsplash.com/photo-1607835017779-c176b83b2dd8?w=700&q=80", type: "Услуга по записи", description: "Бережная поддержка профессионального психолога онлайн. Выберите удобное время для первой встречи.", is_general_offer: false },
  { id: "dms", name: "ДМС Расширенный", category: "Здоровье", supplier: "Ингосстрах", price: 3800, image: "https://images.unsplash.com/photo-1615800001716-c53dd05bf4b8?w=700&q=80", type: "Страхование", description: "Расширенная программа заботы о здоровье: консультации врачей, диагностика и стоматология.", is_general_offer: false },
  { id: "holiday", name: "Дополнительный день отпуска", category: "Отдых", supplier: "Кафетерий льгот", price: 1200, image: "https://images.unsplash.com/photo-1676948242081-17ba7600851a?w=700&q=80", type: "Отпуск", description: "Подарите себе ещё один день для отдыха, путешествия или времени с близкими.", is_general_offer: true },
  { id: "kids", name: "Кружки для детей", category: "Семья", supplier: "Алгоритмика", price: 2100, image: "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=700&q=80", type: "Услуга", description: "Творческие и образовательные занятия для детей: выбирайте то, что нравится именно вашему ребёнку.", is_general_offer: true },
  { id: "conference", name: "Сертификат на конференцию", category: "Обучение", supplier: "Контур", price: 2900, image: "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=700&q=80", type: "С документами", description: "Посетите профессиональное событие и привезите новые идеи своей команде.", is_general_offer: true },
];

const employeeNav = [
  { label: "Главная", icon: Home },
  { label: "Каталог", icon: ShoppingBag },
  { label: "Моё здоровье", icon: HeartPulse },
  { label: "Мои заказы", icon: Package },
  { label: "Баллы и история", icon: Wallet },
  { label: "Новости", icon: BookOpen },
  { label: "Активности", icon: Sparkles },
  { label: "Поддержка", icon: LifeBuoy }
];

const adminNav = [
  { label: "Дашборд", icon: LayoutDashboard },
  { label: "Каталог", icon: ShoppingBag },
  { label: "Сотрудники", icon: Users },
  { label: "Баллы и бюджеты", icon: Wallet },
  { label: "Заказы", icon: Package },
  { label: "Окна выбора", icon: CalendarDays },
  { label: "Коммуникации", icon: Mail },
  { label: "Опросы и активности", icon: Activity },
  { label: "Интеграции", icon: SlidersHorizontal },
  { label: "Отчёты", icon: BarChart3 },
  { label: "Поддержка", icon: LifeBuoy },
  { label: "Аудит", icon: ShieldCheck },
  { label: "Настройки", icon: Settings }
];

const initialOrderRows = [
  { id: "КЛ-24051", name: "Английский для жизни и работы", date: "24 сентября 2025", sum: 2400, status: "В обработке" },
  { id: "КЛ-24012", name: "Подарочная карта Giftery", date: "12 сентября 2025", sum: 1500, status: "Выполнен" },
  { id: "КЛ-23984", name: "Консультация психолога", date: "04 сентября 2025", sum: 1800, status: "На согласовании" },
  { id: "КЛ-23810", name: "ДМС Стандарт", date: "20 августа 2025", sum: 3000, status: "Выполнен" },
];

const initialPeople = [
  { id: "1", name: "Анна Морозова", department: "Продуктовая команда", grade: "Middle", balance: "6 500 б.", status: "Активен" },
  { id: "2", name: "Михаил Соколов", department: "Разработка", grade: "Senior", balance: "8 200 б.", status: "Активен" },
  { id: "3", name: "Екатерина Волкова", department: "Маркетинг", grade: "Middle", balance: "3 750 б.", status: "Активен" },
  { id: "4", name: "Дмитрий Козлов", department: "Финансы", grade: "Lead", balance: "11 000 б.", status: "Активен" },
  { id: "5", name: "Мария Петрова", department: "HR", grade: "Middle", balance: "5 400 б.", status: "Исключение" },
];

function ProductCard({ item, inCart, onOpen, onAdd }: { item: Product; inCart: boolean; onOpen: () => void; onAdd: () => void }) {
  return (
    <article className="product-card">
      <button className="product-image" onClick={onOpen} aria-label={`Открыть ${item.name}`}>
        <img src={item.image} alt={item.name} />
        {item.tag && <span className="image-tag">{item.tag}</span>}
      </button>
      <div className="product-content">
        <span className="eyebrow">{item.category} <span className="dot">·</span> {item.supplier}</span>
        <button className="product-title" onClick={onOpen}>{item.name}</button>
        <div className="product-bottom">
          <span className="price"><Coins size={17} />{points(item.price)}</span>
          <IconButton
            className={inCart ? "added" : "add-product"}
            label={inCart ? "В корзине" : "В корзину"}
            onClick={onAdd}
          >
            {inCart ? <Check size={19} /> : <Plus size={19} />}
          </IconButton>
        </div>
      </div>
    </article>
  );
}

function SectionHeading({ title, action, onAction, subtitle }: { title: string; action?: string; onAction?: () => void; subtitle?: string }) {
  return (
    <div className="section-heading">
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action && <LinkButton onClick={onAction ?? (() => {})}>{action}</LinkButton>}
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState<"employee" | "admin">("employee");
  const [page, setPage] = useState("Главная");
  const [adminPage, setAdminPage] = useState("Дашборд");
  const [productsList, setProductsList] = useState<Product[]>(initialProducts);
  const [selected, setSelected] = useState<Product>(initialProducts[0]);
  const [cart, setCart] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("Все категории");
  const [sort, setSort] = useState("Популярное");
  const [modal, setModal] = useState("");
  const [toast, setToast] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [role, setRole] = useState("Сотрудник");
  const [onboardingStep, setOnboardingStep] = useState(0);
  const [packageItems, setPackageItems] = useState([true, true, false]);
  const [healthTab, setHealthTab] = useState("Что входит");
  const [detailTab, setDetailTab] = useState("Описание");
  const [quantity, setQuantity] = useState(1);
  const [amount, setAmount] = useState("1000");
  const [otp, setOtp] = useState("");
  const [name, setName] = useState("");
  const [activeOrder, setActiveOrder] = useState(initialOrderRows[0]);
  const [loading, setLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState(false);
  const [windowClosed, setWindowClosed] = useState(false);
  const [birthday, setBirthday] = useState("");
  const [donation, setDonation] = useState(1500);
  const [balance, setBalance] = useState(6500);
  const [settings, setSettings] = useState<Record<string, boolean>>({
    "Лотерея": true,
    "Командные сборы": true,
    "Перевод баллов": true,
    "Благотворительность": true,
    "Соцпроекты": true,
    "Стартовый пакет": true,
    "Колесо баланса": true,
    "Тур": true
  });

  // Load from backend API if available
  useEffect(() => {
    api.getMe()
      .then(profile => {
        if (profile) {
          setBalance(profile.available_balance || 6500);
          if (profile.role === 'admin') setRole("Администратор");
          else if (profile.role === 'hr') setRole("HR");
          else if (profile.role === 'vip') setRole("ВИП");
          else if (profile.role === 'maternity') setRole("Декрет");
          else if (profile.role === 'exclusion') setRole("Exclusion");
          else setRole("Сотрудник");
        }
      })
      .catch(() => {
        // standalone mode fallback
      });

    api.getCatalog()
      .then(res => {
        const items = res.results || res;
        if (Array.isArray(items) && items.length > 0) {
          const mapped = items.map((p: any) => ({
            id: p.slug || String(p.id),
            name: p.name,
            category: p.category,
            supplier: p.supplier,
            price: p.price,
            image: p.image || "https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=700&q=80",
            tag: p.tag,
            type: p.product_type,
            description: p.description,
            is_general_offer: p.is_general_offer
          }));
          setProductsList(mapped);
          setSelected(mapped[0]);
        }
      })
      .catch(() => {});
  }, []);

  const cartProducts = cart.map(id => productsList.find(p => p.id === id)!).filter(Boolean);
  const cartTotal = cartProducts.reduce((sum, item) => sum + item.price, 0);
  const packageTotal = packageItems.reduce((sum, on, i) => sum + (on ? [3000, 2400, 1800][i] : 0), 0);

  const go = (destination: string) => { setPage(destination); setMobileMenu(false); window.scrollTo(0, 0); };
  const goAdmin = (destination: string) => { setAdminPage(destination); window.scrollTo(0, 0); };
  const openProduct = (p: Product) => { setSelected(p); setDetailTab("Описание"); go("Карточка позиции"); };
  const addProduct = (p: Product) => {
    if (cart.includes(p.id)) {
      go("Корзина");
    } else {
      setCart([...cart, p.id]);
      setToast(`${p.name} добавлено в корзину`);
      api.addToCart(p.id, 1).catch(() => {});
    }
  };
  const showLoading = () => { setLoading(true); setTimeout(() => setLoading(false), 800); };
  const switchMode = () => {
    setMode(mode === "employee" ? "admin" : "employee");
    setModal("");
    window.scrollTo(0, 0);
  };

  const handleCheckoutSubmit = async () => {
    if (checkoutError) {
      go("Ошибка оформления");
      return;
    }
    try {
      await api.checkout(cartProducts.map(p => ({ product_id: p.id, quantity: 1 })));
      setBalance(Math.max(0, balance - cartTotal));
    } catch {
      // Offline fallback
      setBalance(Math.max(0, balance - cartTotal));
    }
    setCart([]);
    go("Заказ оформлен");
  };

  const hero = (
    <section className="hero">
      <div className="hero-copy">
        <span className="hero-kicker"><Sparkles size={15} /> ВАШИ ВОЗМОЖНОСТИ</span>
        <h1>Больше хорошего<br />каждый день</h1>
        <p>Выбирайте то, что делает жизнь лучше. Ваши баллы — ваши возможности.</p>
        <Button onClick={() => go("Каталог")}>Выбрать льготы <ArrowRight size={17} /></Button>
        <span className="hero-footnote">Окно выбора открыто до 15 октября</span>
      </div>
      <div className="hero-art">
        <div className="art-orbit orbit-one" />
        <div className="art-orbit orbit-two" />
        <div className="art-circle circle-back" />
        <div className="art-circle circle-main"><Gift size={124} strokeWidth={1.25} /></div>
        <div className="floating-card float-heart"><Heart size={23} fill="currentColor" /></div>
        <div className="floating-card float-star"><Sparkles size={22} /></div>
        <div className="floating-label">
          <span className="mini-coin"><Coins size={17} /></span>
          <span>На то, что важно<br /><strong>именно вам</strong></span>
        </div>
      </div>
    </section>
  );

  const home = (
    <>
      <div className="greeting">
        <div>
          <span className="overline">СРЕДА, 24 СЕНТЯБРЯ</span>
          <h1>Доброе утро, Анна <Sparkles className="wave" size={25} /></h1>
          <p>Время выбрать что-то приятное для себя</p>
        </div>
        <Badge tone={windowClosed ? "warning" : "success"}>
          <span className="status-dot" /> Окно выбора {windowClosed ? "закрыто" : "открыто"}
        </Badge>
      </div>

      {windowClosed && (
        <Alert tone="warning" title="Окно выбора закрыто">
          Изменения сейчас недоступны. Чтобы изменить льготы, подайте заявку в HR.
        </Alert>
      )}

      {hero}

      <div className="home-overview">
        <div className="overview-balance">
          <div className="overview-top">
            <div className="overview-icon"><Coins size={22} /></div>
            <span>ВАШ БАЛАНС</span>
            <MoreHorizontal size={20} />
          </div>
          <div className="overview-number">{balance.toLocaleString("ru-RU")} <small>баллов</small></div>
          <p>Доступно для покупок</p>
          <Progress value={balance} max={10000} />
          <div className="overview-meta">
            <span>Использовано {(10000 - balance).toLocaleString("ru-RU")} б.</span>
            <span>Всего 10 000 б.</span>
          </div>
          <button className="text-action" onClick={() => go("Баллы и история")}>
            История баллов <ArrowRight size={16} />
          </button>
        </div>

        <div className="overview-window">
          <div className="overview-icon warm"><CalendarDays size={22} /></div>
          <span className="overline">УСПЕЙТЕ ВЫБРАТЬ</span>
          <h3>Ещё 21 день<br />до конца окна</h3>
          <p>После 15 октября выбор льгот будет временно недоступен.</p>
          <button className="text-action" onClick={() => go("Каталог")}>
            Смотреть каталог <ArrowRight size={16} />
          </button>
        </div>

        <div className="overview-health">
          <div className="overview-icon blue"><HeartPulse size={22} /></div>
          <span className="overline">МОЁ ЗДОРОВЬЕ</span>
          <h3>Забота рядом</h3>
          <p>Ваш полис ДМС действует до 31 декабря 2025 года.</p>
          <div className="health-status"><span className="status-dot" /> Полис активен</div>
          <button className="text-action" onClick={() => go("Моё здоровье")}>
            Мой полис <ArrowRight size={16} />
          </button>
        </div>
      </div>

      <div className="section-block">
        <SectionHeading
          title="Рекомендуем вам"
          subtitle="Подобрали льготы, которые могут вам понравиться"
          action="Весь каталог"
          onAction={() => go("Каталог")}
        />
        <div className="product-grid">
          {productsList.slice(0, 4).map(p => (
            <ProductCard
              key={p.id}
              item={p}
              inCart={cart.includes(p.id)}
              onOpen={() => openProduct(p)}
              onAdd={() => addProduct(p)}
            />
          ))}
        </div>
      </div>

      <div className="home-bottom">
        <div className="expire-card">
          <span className="expire-icon"><Clock3 size={23} /></span>
          <div>
            <h3>Баллы скоро сгорят</h3>
            <p><strong>800 баллов</strong> действуют до 24 октября. Найдите им применение!</p>
          </div>
          <Button variant="secondary" onClick={() => go("Каталог")}>Выбрать льготу</Button>
        </div>
        <div className="news-card">
          <span className="overline">НОВОСТИ</span>
          <h3>Новое в вашем кафетерии</h3>
          <p>Добавили возможности для отдыха и обучения этой осенью.</p>
          <LinkButton onClick={() => go("Новости")}>Читать новости</LinkButton>
        </div>
      </div>

      <div className="section-block">
        <SectionHeading title="Популярное сейчас" action="Смотреть всё" onAction={() => go("Каталог")} />
        <div className="product-grid">
          {productsList.slice(4, 8).map(p => (
            <ProductCard
              key={p.id}
              item={p}
              inCart={cart.includes(p.id)}
              onOpen={() => openProduct(p)}
              onAdd={() => addProduct(p)}
            />
          ))}
        </div>
      </div>
    </>
  );

  const catalogList = productsList.filter(p => {
    const matchesCategory = category === "Все категории" || p.category === category;
    const matchesSearch = `${p.name} ${p.supplier}`.toLowerCase().includes(search.toLowerCase());
    const vipFilter = !(role === "ВИП" && !p.is_general_offer);
    const maternityFilter = !(role === "Декрет" && p.category === "Здоровье");
    return matchesCategory && matchesSearch && vipFilter && maternityFilter;
  }).sort((a, b) => {
    if (sort === "Сначала дешевле") return a.price - b.price;
    if (sort === "Сначала дороже") return b.price - a.price;
    return 0;
  });

  const catalog = (
    <>
      <Breadcrumbs items={["Главная", "Каталог"]} onClick={() => go("Главная")} />
      <div className="page-heading">
        <div>
          <span className="overline">НАЙДИТЕ СВОЁ</span>
          <h1>Каталог льгот</h1>
          <p>Всё, что делает рабочие дни и жизнь за их пределами лучше</p>
        </div>
        <span className="result-count">{catalogList.length} предложений</span>
      </div>

      <div className="catalog-layout">
        <aside className="filter-panel">
          <div className="filter-heading">
            <h3>Фильтры</h3>
            <SlidersHorizontal size={18} />
          </div>
          <div className="filter-group">
            <strong>Категории</strong>
            {["Все категории", "Здоровье", "Обучение", "Отдых", "Подарки", "Семья"].map(c => (
              <button
                className={`filter-option ${category === c ? "current" : ""}`}
                key={c}
                onClick={() => setCategory(c)}
              >
                {c}
                <span>{c === "Все категории" ? productsList.length : productsList.filter(p => p.category === c).length}</span>
              </button>
            ))}
          </div>
          <div className="filter-group">
            <strong>Стоимость в баллах</strong>
            <div className="range-label"><span>0 б.</span><span>5 000 б.</span></div>
            <Slider value={5000} max={5000} onChange={() => {}} />
          </div>
          <div className="filter-group">
            <strong>Доступность</strong>
            <Checkbox checked={true} onChange={() => {}} label="Доступно мне" />
          </div>
          <button className="reset-filters" onClick={() => { setCategory("Все категории"); setSearch(""); }}>
            Сбросить фильтры
          </button>
        </aside>

        <div className="catalog-content">
          <div className="catalog-toolbar">
            <SearchField value={search} onChange={setSearch} placeholder="Поиск по названию или поставщику" />
            <Select value={sort} onChange={setSort} options={["Популярное", "Сначала дешевле", "Сначала дороже"]} />
          </div>

          {role !== "Сотрудник" && (
            <Alert tone="info">
              {role === "Декрет"
                ? "Страховые программы недоступны для вашего сегмента (РОЛ.1, ФТ-ДМС)."
                : role === "ВИП"
                ? "Для роли ВИП доступны только общие предложения компании (РОЛ.1)."
                : `Режим роли: ${role}`}
            </Alert>
          )}

          {catalogList.length ? (
            <div className="product-grid catalog-grid">
              {catalogList.map(p => (
                <ProductCard
                  key={p.id}
                  item={p}
                  inCart={cart.includes(p.id)}
                  onOpen={() => openProduct(p)}
                  onAdd={() => addProduct(p)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              title="Ничего не нашлось"
              text="Попробуйте изменить запрос или сбросить фильтры."
              action="Сбросить фильтры"
              onAction={() => { setSearch(""); setCategory("Все категории"); }}
            />
          )}
        </div>
      </div>
    </>
  );

  const productDetail = (
    <>
      <Breadcrumbs items={["Главная", "Каталог", selected.category, selected.name]} onClick={i => go(i === 0 ? "Главная" : "Каталог")} />
      <div className="detail-layout">
        <div className="detail-main">
          <div className="detail-image"><img src={selected.image} alt={selected.name} /></div>
          <Tabs items={["Описание", "Условия", "Документы"]} value={detailTab} onChange={setDetailTab} />
          <div className="detail-copy">
            {detailTab === "Описание" ? (
              <>
                <h3>О льготе</h3>
                <p>{selected.description}</p>
                <p>Это предложение создано, чтобы вы могли посвятить больше времени тому, что по-настоящему важно.</p>
              </>
            ) : detailTab === "Условия" ? (
              <>
                <h3>Условия использования</h3>
                <p>Льгота доступна сотрудникам с активным балансом. После оформления заказа подробная инструкция появится в разделе «Мои заказы».</p>
                <Alert tone="info">Осталось 2 из 3 заказов в этом месяце</Alert>
              </>
            ) : (
              <>
                <h3>Документы</h3>
                <div className="file-item"><FileText size={18} /> Условия предоставления.pdf <Download size={16} /></div>
              </>
            )}
          </div>
        </div>

        <aside className="detail-side">
          <span className="eyebrow">{selected.category} · {selected.supplier}</span>
          <h1>{selected.name}</h1>
          <Badge tone="success"><span className="status-dot" /> Доступно для заказа</Badge>
          <div className="detail-price"><Coins size={25} /> {points(selected.price)}</div>
          <p className="detail-note">Баллы спишутся после подтверждения заказа</p>
          <div className="detail-divider" />

          {selected.type === "Проживание" && (
            <div className="detail-fields">
              <div className="field-pair">
                <DateField label="Заезд" value={birthday} onChange={setBirthday} />
                <DateField label="Выезд" value={name} onChange={setName} />
              </div>
              <Field label="Гостей" type="number" value={String(quantity)} onChange={v => setQuantity(Number(v))} />
              <small>Бронирование не позднее чем за 7 дней до заезда (ФТ-КАТ.7)</small>
            </div>
          )}

          {selected.type === "Услуга по записи" && (
            <div className="detail-fields">
              <DateField label="Выберите дату консультации" value={birthday} onChange={setBirthday} />
              <div className="slot-row">
                <button>10:00</button>
                <button>13:30</button>
                <button>17:00</button>
              </div>
            </div>
          )}

          {selected.type === "Сертификат" && (
            <div className="detail-fields">
              <Select label="Номинал" value="1 500 б." onChange={() => {}} options={["1 500 б.", "3 000 б."]} />
              <Field label="Получатель" placeholder="Имя или email" />
            </div>
          )}

          {selected.type === "Отпуск" && (
            <div className="detail-fields">
              <Field label="Количество дней" type="number" value={String(quantity)} onChange={v => setQuantity(Number(v))} />
              <Alert tone="warning">Требуется согласование руководителя и HR (ФТ-ЛГТ.4)</Alert>
            </div>
          )}

          {selected.type === "С документами" && <FileUploader label="Приложить подтверждающие документы" />}

          <Button className="full" onClick={() => addProduct(selected)}>
            {cart.includes(selected.id) ? "Перейти в корзину" : "Добавить в корзину"} <ArrowRight size={17} />
          </Button>
          <p className="fine-print"><ShieldCheck size={15} /> Безопасное оформление внутри компании</p>
        </aside>
      </div>
    </>
  );

  const cartPage = (
    <>
      <Breadcrumbs items={["Главная", "Корзина"]} onClick={() => go("Главная")} />
      <div className="page-heading">
        <div>
          <span className="overline">ПОЧТИ ГОТОВО</span>
          <h1>Корзина <span className="heading-muted">{cart.length}</span></h1>
          <p>Проверьте выбранные льготы перед оформлением</p>
        </div>
      </div>

      {cart.length ? (
        <div className="split-layout">
          <div className="cart-list">
            {cartProducts.map(p => (
              <div className="cart-item" key={p.id}>
                <img src={p.image} alt="" />
                <div>
                  <span className="eyebrow">{p.category} · {p.supplier}</span>
                  <h3>{p.name}</h3>
                  <span className="price"><Coins size={16} />{points(p.price)}</span>
                </div>
                <IconButton label="Удалить" onClick={() => setCart(cart.filter(id => id !== p.id))}>
                  <Trash2 size={18} />
                </IconButton>
              </div>
            ))}
            <Alert tone="info" title="Сгораемые баллы спишутся первыми">
              У вас есть 800 б., которые действуют до 24 октября (правило FIFO).
            </Alert>
          </div>

          <aside className="summary-card">
            <h3>Ваш заказ</h3>
            <div className="summary-row"><span>Льготы ({cart.length})</span><strong>{points(cartTotal)}</strong></div>
            <div className="summary-row"><span>Доступно баллов</span><strong>{points(balance)}</strong></div>
            <div className="summary-row total">
              <span>Останется после покупки</span>
              <strong>{points(balance - cartTotal)}</strong>
            </div>

            {cartTotal > balance && (
              <Alert tone="danger">Превышение на {points(cartTotal - balance)}. Скорректируйте набор.</Alert>
            )}

            <Button
              className="full"
              disabled={cartTotal > balance || windowClosed}
              onClick={() => go("Подтверждение")}
            >
              Перейти к оформлению <ArrowRight size={17} />
            </Button>
            <p className="fine-print">Оформление не требует оплаты деньгами</p>
          </aside>
        </div>
      ) : (
        <EmptyState
          title="В корзине пока пусто"
          text="Посмотрите каталог и добавьте то, что вам понравится."
          action="Перейти в каталог"
          onAction={() => go("Каталог")}
        />
      )}
    </>
  );

  const checkout = (
    <div className="center-flow">
      <Stepper steps={["Корзина", "Подтверждение", "Готово"]} active={page === "Подтверждение" ? 1 : 2} />
      {page === "Подтверждение" ? (
        <>
          <h1>Подтвердите заказ</h1>
          <p>Проверьте детали — после оформления мы пришлём уведомление.</p>
          <div className="flow-card">
            {cartProducts.map(p => (
              <div className="summary-row" key={p.id}>
                <span>{p.name}</span>
                <strong>{points(p.price)}</strong>
              </div>
            ))}
            <div className="summary-row total">
              <span>Итого</span>
              <strong>{points(cartTotal)}</strong>
            </div>
          </div>
          <Button className="full" onClick={handleCheckoutSubmit}>
            Подтвердить заказ <ArrowRight size={17} />
          </Button>
          <button className="subtle-link" onClick={() => go("Корзина")}>Вернуться в корзину</button>
        </>
      ) : (
        <>
          <div className={`success-symbol ${page === "Ошибка оформления" ? "error" : ""}`}>
            {page === "Ошибка оформления" ? <X size={35} /> : <Check size={35} />}
          </div>
          <h1>{page === "Ошибка оформления" ? "Не получилось оформить заказ" : "Заказ оформлен!"}</h1>
          <p>{page === "Ошибка оформления" ? "Попробуйте ещё раз. Ваши баллы не списаны." : "Заказ № КЛ-24052 уже в работе. Статус всегда можно посмотреть в разделе «Мои заказы»."}</p>
          <Button onClick={() => go(page === "Ошибка оформления" ? "Корзина" : "Мои заказы")}>
            {page === "Ошибка оформления" ? "Попробовать снова" : "Перейти к заказам"} <ArrowRight size={17} />
          </Button>
        </>
      )}
    </div>
  );

  const health = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">ЗАБОТА О ВАС</span>
          <h1>Моё здоровье</h1>
          <p>Вся информация о вашем полисе и возможностях программы (ФТ-ДМС)</p>
        </div>
      </div>

      {role === "Декрет" ? (
        <Alert tone="info" title="Страховые программы недоступны">
          Для вашей роли (Декрет) этот раздел временно недоступен в соответствии с правилами программы (РОЛ.1, ФТ-ДМС). Обратитесь в HR, если у вас есть вопросы.
        </Alert>
      ) : (
        <>
          <div className="health-hero">
            <div>
              <span className="light-kicker">ВАШ ПОЛИС ДМС</span>
              <h2>Здоровье в надёжных руках</h2>
              <p>Программа «ДМС Стандарт» · Ингосстрах</p>
              <Badge tone="success">Действует до 31 декабря 2025</Badge>
            </div>
            <div className="health-emblem"><HeartPulse size={70} strokeWidth={1.2} /></div>
          </div>

          <div className="health-layout">
            <div className="surface-card">
              <SectionHeading title="Ваша программа" />
              <Tabs items={["Что входит", "Что не входит", "Клиники"]} value={healthTab} onChange={setHealthTab} />
              <div className="health-features">
                {(healthTab === "Что входит"
                  ? ["Приём терапевта и профильных специалистов", "Диагностика и лабораторные исследования", "Телемедицина 24/7", "Экстренная медицинская помощь"]
                  : healthTab === "Что не входит"
                  ? ["Косметологические процедуры", "Плановая госпитализация", "Стоматология (можно подключить отдельно)"]
                  : ["Клиника «Медси» · ул. Красная, 14", "Клиника «Семейная» · пр. Мира, 28", "Диагностический центр «Здоровье»"]
                ).map(t => (
                  <div key={t}><span className="feature-check"><Check size={15} /></span>{t}</div>
                ))}
              </div>
              <div className="detail-hint"><FileCheck2 size={17} /> Оформление полиса завершено — все документы готовы</div>
            </div>

            <div className="health-actions">
              <div className="surface-card">
                <h3>Больше возможностей</h3>
                <p>Подстройте заботу о здоровье под себя и близких.</p>
                <div className="action-row">
                  <span className="action-icon"><Plus size={19} /></span>
                  <div><strong>Добавить члена семьи</strong><small>Оформить полис для близкого человека</small></div>
                  <IconButton label="Открыть" onClick={() => setModal("family")}><ChevronRight size={19} /></IconButton>
                </div>
                <div className="action-row">
                  <span className="action-icon"><Heart size={19} /></span>
                  <div><strong>Расширить пакет</strong><small>Стоматология, диагностика и другое</small></div>
                  <IconButton label="Открыть" onClick={() => setModal("upgrade")}><ChevronRight size={19} /></IconButton>
                </div>
                <div className="action-row">
                  <span className="action-icon"><SlidersHorizontal size={19} /></span>
                  <div><strong>Заменить программу</strong><small>Сравнить доступные варианты</small></div>
                  <IconButton label="Открыть" onClick={() => setModal("upgrade")}><ChevronRight size={19} /></IconButton>
                </div>
              </div>
              <button className="subtle-link" onClick={() => setModal("decline")}>Отказаться от базового ДМС (ФТ-ДМС.8)</button>
            </div>
          </div>
        </>
      )}
    </>
  );

  const orders = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">ВАШИ ПОКУПКИ</span>
          <h1>Мои заказы</h1>
          <p>Все выбранные льготы и их статусы в одном месте</p>
        </div>
      </div>
      <div className="surface-card table-card">
        <div className="table-toolbar">
          <SearchField value={search} onChange={setSearch} placeholder="Номер или название заказа" />
          <Select
            value={sort === "Популярное" ? "Все статусы" : sort}
            onChange={setSort}
            options={["Все статусы", "В обработке", "Выполнен", "На согласовании", "Отменён"]}
          />
        </div>
        <DataTable
          rows={initialOrderRows.filter(o =>
            (sort === "Популярное" || sort === "Все статусы" || o.status === sort) &&
            `${o.id} ${o.name}`.toLowerCase().includes(search.toLowerCase())
          )}
          columns={[
            { key: "id", label: "Заказ" },
            { key: "name", label: "Льгота" },
            { key: "date", label: "Дата" },
            { key: "sum", label: "Сумма", render: r => <span className="price"><Coins size={15} />{points(r.sum)}</span> },
            { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Выполнен" ? "success" : "warning"}>{r.status}</Badge> }
          ]}
          onRow={r => { setActiveOrder(r); setModal("order"); }}
        />
      </div>
    </>
  );

  const pointsPage = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">ВАШИ ВОЗМОЖНОСТИ</span>
          <h1>Баллы и история</h1>
          <p>Следите за балансом и используйте баллы с пользой</p>
        </div>
      </div>
      <div className="points-overview">
        <div className="points-primary">
          <span className="light-kicker">ДОСТУПНО СЕЙЧАС</span>
          <div className="big-points"><Coins size={32} />{points(balance)}</div>
          <p>Из 10 000 баллов годового бюджета</p>
          <Progress value={balance} max={10000} />
        </div>
        <div className="points-mini">
          <span className="overline">СГОРАЕМЫЕ</span>
          <h3>800 б.</h3>
          <p>До 24 октября 2025</p>
          <Badge tone="warning">Через 30 дней</Badge>
        </div>
        <div className="points-mini">
          <span className="overline">НЕСГОРАЕМЫЕ</span>
          <h3>5 700 б.</h3>
          <p>Доступны без срока</p>
          <Badge tone="success">Всегда с вами</Badge>
        </div>
      </div>
      <div className="points-layout">
        <div className="surface-card">
          <SectionHeading title="История операций" />
          <div className="operations">
            {[
              { t: "Начисление за стаж", d: "20 сентября 2025 · 3 года с нами", v: "+1 500 б.", icon: Sparkles },
              { t: "Годовое начисление", d: "01 сентября 2025 · Бюджет льгот", v: "+5 000 б.", icon: Gift },
              { t: "Английский для жизни и работы", d: "24 августа 2025 · Заказ КЛ-23810", v: "−2 400 б.", icon: BookOpen },
              { t: "Подарок ко дню рождения", d: "12 августа 2025 · От компании", v: "+500 б.", icon: Heart }
            ].map(row => (
              <div className="operation" key={row.t}>
                <span className="operation-icon"><row.icon size={19} /></span>
                <div><strong>{row.t}</strong><small>{row.d}</small></div>
                <b className={row.v.startsWith("+") ? "positive" : ""}>{row.v}</b>
              </div>
            ))}
          </div>
        </div>

        <aside className="points-side">
          <div className="surface-card">
            <h3>Поделиться баллами</h3>
            <p>Порадуйте коллегу небольшим знаком внимания (комиссия 25%).</p>
            <Button variant="secondary" className="full" onClick={() => setModal("transfer")}>
              Перевести баллы <ArrowRight size={16} />
            </Button>
          </div>
          <div className="surface-card charity-card">
            <span className="charity-icon"><Heart size={22} /></span>
            <h3>Добро умножается</h3>
            <p>Поддержите благотворительный фонд. Компания добавит столько же (1x).</p>
            <Button variant="ghost" onClick={() => setModal("charity")}>
              Помочь вместе <ArrowRight size={16} />
            </Button>
          </div>
        </aside>
      </div>
    </>
  );

  const news = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">БУДЬТЕ В КУРСЕ</span>
          <h1>Новости</h1>
          <p>Всё важное и интересное в вашем кафетерии</p>
        </div>
      </div>
      <div className="editorial-grid">
        <article className="news-feature">
          <img src="https://images.unsplash.com/photo-1619688137428-851529e61a0f?w=1100&q=80" alt="Домик у озера" />
          <div>
            <Badge tone="success">Новое</Badge>
            <h2>Осень — время для маленьких путешествий</h2>
            <p>В каталоге появились уютные выходные на базе отдыха «Лес и озеро».</p>
            <LinkButton onClick={() => openProduct(initialProducts[1])}>Смотреть предложение</LinkButton>
          </div>
        </article>
        <div className="news-stack">
          {["Окно выбора льгот открыто до 15 октября", "Знакомьтесь: новые курсы английского", "Как работают сгораемые баллы"].map((t, i) => (
            <button className="news-list-item" key={t} onClick={() => setModal("news")}>
              <span className="overline">{i === 0 ? "24 СЕНТЯБРЯ" : "18 СЕНТЯБРЯ"}</span>
              <h3>{t}</h3>
              <span>Читать новость <ArrowRight size={15} /></span>
            </button>
          ))}
        </div>
      </div>
    </>
  );

  const activities = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">УЧАСТВУЙТЕ И ВДОХНОВЛЯЙТЕСЬ</span>
          <h1>Активности</h1>
          <p>Новые поводы быть вместе и узнавать друг друга</p>
        </div>
      </div>
      <div className="feature-grid">
        <div className="surface-card activity-card">
          <span className="activity-illustration"><ClipboardList size={40} /></span>
          <Badge tone="info">Опрос · 3 минуты</Badge>
          <h3>Что для вас важно в льготах?</h3>
          <p>Помогите сделать кафетерий ещё полезнее для каждого.</p>
          <Progress value={40} />
          <Button onClick={() => setModal("survey")}>Продолжить опрос</Button>
        </div>
        <div className="surface-card activity-card">
          <span className="activity-illustration peach"><Gift size={40} /></span>
          <Badge tone="warning">До 15 октября</Badge>
          <h3>Осенняя лотерея</h3>
          <p>Призовой фонд — 30 000 баллов. Результаты объявим после окончания окна.</p>
          <Button variant="secondary" onClick={() => setModal("lottery")}>Подробнее</Button>
        </div>
      </div>
    </>
  );

  const support = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">МЫ РЯДОМ</span>
          <h1>Поддержка</h1>
          <p>Поможем разобраться с любым вопросом (норматив SLA: 24 часа)</p>
        </div>
        <Button onClick={() => setModal("ticket")}><Plus size={17} /> Новое обращение</Button>
      </div>
      <div className="support-layout">
        <div className="surface-card">
          <SectionHeading title="Ваши обращения" />
          <div className="action-row">
            <span className="action-icon"><LifeBuoy size={19} /></span>
            <div><strong>КЛ-1842 · Вопрос по сертификату</strong><small>22 сентября 2025 · В обработке</small></div>
            <Badge tone="warning">В работе</Badge>
          </div>
          <div className="action-row">
            <span className="action-icon"><Check size={19} /></span>
            <div><strong>КЛ-1720 · Изменение данных</strong><small>10 августа 2025 · Решено</small></div>
            <Badge tone="success">Решено</Badge>
          </div>
        </div>
        <div className="surface-card support-help">
          <CircleHelp size={30} />
          <h3>Есть идея для новой льготы?</h3>
          <p>Расскажите, что хотели бы видеть в каталоге (ФТ-ПОД.5).</p>
          <Button variant="secondary" onClick={() => setModal("suggestion")}>Предложить льготу</Button>
        </div>
      </div>
    </>
  );

  const profile = (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">ЛИЧНЫЙ КАБИНЕТ</span>
          <h1>Мой профиль</h1>
          <p>Ваши данные и настройки доступа</p>
        </div>
      </div>
      <div className="profile-layout">
        <div className="surface-card">
          <div className="profile-head">
            <Avatar name="АМ" />
            <div>
              <h2>Анна Морозова</h2>
              <p>Продуктовая команда · Грейд Middle</p>
            </div>
          </div>
          <div className="profile-line"><span>Корпоративная почта</span><strong>a.morozova@company.ru</strong></div>
          <div className="profile-line">
            <span>Роль</span>
            <Select value={role} onChange={setRole} options={["Сотрудник", "Декрет", "ВИП", "HR", "Администратор", "Exclusion"]} />
          </div>
          <div className="profile-line"><span>Активная нефинансовая льгота</span><strong>Гибкий график (ФТ-ЛГТ.5)</strong></div>
        </div>
        <div className="surface-card">
          <h3>Мои документы</h3>
          <p>Документы и справки, связанные с вашими льготами.</p>
          <div className="file-item"><FileText size={18} /> Полис ДМС.pdf <Download size={16} /></div>
        </div>
      </div>
    </>
  );

  const exclusionScreen = (
    <div className="center-flow py-16 text-center max-w-lg mx-auto">
      <div className="mx-auto w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mb-6">
        <AlertTriangle size={36} />
      </div>
      <h1 className="text-2xl font-bold mb-2">Доступ ограничен</h1>
      <p className="text-gray-600 mb-8 leading-relaxed">
        Ваша учётная запись находится в сегменте Exclusion. Доступ к витрине и балансу временно приостановлен. Пожалуйста, обратитесь в отдел HR для уточнения статуса.
      </p>
      <div className="flex flex-col gap-3">
        <Button onClick={() => setModal("ticket")}>Написать обращение в HR</Button>
        <button className="subtle-link" onClick={() => setRole("Сотрудник")}>Переключить на роль «Сотрудник» (Демо)</button>
      </div>
      <DeveloperCredit className="mt-12" />
    </div>
  );

  const login = (
    <div className="auth-page">
      <div className="auth-aside">
        <span className="brand-mark"><Gift size={26} /></span>
        <h1>Всё хорошее<br />в одном месте.</h1>
        <p>Льготы, которые действительно подходят вам.</p>
        <div className="auth-decoration"><span /><span /><span /></div>
      </div>
      <div className="auth-main">
        <div className="auth-card">
          <span className="overline">ДОБРО ПОЖАЛОВАТЬ</span>
          <h1>{page === "Нет в базе" ? "Не нашли вас в базе" : "Войдите в кафетерий"}</h1>
          <p>
            {page === "Нет в базе"
              ? "Похоже, данные ещё не синхронизировались. Напишите команде HR — мы поможем разобраться."
              : "Вход через корпоративную учётную запись. Ваши льготы уже ждут вас."}
          </p>
          <Button className="full" onClick={() => go(page === "Нет в базе" ? "Поддержка" : "Онбординг")}>
            {page === "Нет в базе" ? "Написать в HR" : "Войти через корпоративный SSO"} <ArrowRight size={17} />
          </Button>
          <button className="subtle-link" onClick={() => go(page === "Нет в базе" ? "Вход" : "Нет в базе")}>
            {page === "Нет в базе" ? "Вернуться ко входу" : "Не могу войти (рассинхронизация)"}
          </button>
          <DeveloperCredit className="mt-6" />
        </div>
      </div>
    </div>
  );

  const onboarding = (
    <div className="onboarding-page">
      <div className="onboarding-brand">
        <span className="brand-mark"><Gift size={21} /></span> кафетерий<span>льгот</span>
      </div>
      <div className="onboarding-inner">
        <Stepper steps={["Знакомство", "Интересы", "Ваш пакет"]} active={onboardingStep} />
        {onboardingStep === 0 ? (
          <>
            <span className="overline">ДОБРО ПОЖАЛОВАТЬ, АННА</span>
            <h1>Ваш бюджет уже готов.<br />Пора выбрать своё.</h1>
            <p>Мы начислили вам баллы на льготы. Расскажите немного о себе — и мы подберём то, что вам подходит.</p>
            <div className="onboard-balance"><Coins size={27} /><strong>6 500 б.</strong><span>ваш стартовый баланс</span></div>
            <Button onClick={() => setOnboardingStep(1)}>Выбрать льготы <ArrowRight size={17} /></Button>
          </>
        ) : onboardingStep === 1 ? (
          <>
            <span className="overline">ШАГ 2 ИЗ 3</span>
            <h1>Что для вас сейчас важнее?</h1>
            <p>Выберите то, что откликается. Ответы помогут нам составить рекомендации.</p>
            <div className="answer-grid">
              {[
                { icon: HeartPulse, label: "Здоровье и забота" },
                { icon: BookOpen, label: "Развитие и обучение" },
                { icon: Gift, label: "Подарки и впечатления" },
                { icon: Home, label: "Отдых и семья" }
              ].map((a, i) => (
                <button
                  className={`answer-card ${packageItems[i % 3] ? "chosen" : ""}`}
                  key={a.label}
                  onClick={() => setPackageItems(packageItems.map((v, j) => j === i % 3 ? !v : v))}
                >
                  <a.icon size={25} />{a.label}<Check size={17} />
                </button>
              ))}
            </div>
            <Button onClick={() => setOnboardingStep(2)}>Продолжить <ArrowRight size={17} /></Button>
          </>
        ) : (
          <>
            <span className="overline">ВАШ СТАРТОВЫЙ ПАКЕТ</span>
            <h1>Мы подобрали для вас</h1>
            <p>Можно принять пакет целиком или настроить его под себя.</p>
            <div className="package-list">
              {[initialProducts[4], initialProducts[0], initialProducts[3]].map((p, i) => (
                <div className="package-row" key={p.id}>
                  <img src={p.image} alt="" />
                  <div><strong>{p.name}</strong><small>{points([3000, 2400, 1800][i])}</small></div>
                  <Toggle checked={packageItems[i]} onChange={v => setPackageItems(packageItems.map((item, j) => j === i ? v : item))} />
                </div>
              ))}
            </div>
            <div className="package-total">
              <span>Останется после выбора</span>
              <strong>{points(balance - packageTotal)}</strong>
            </div>
            {packageTotal > balance && (
              <Alert tone="danger" title={`Превышение на ${points(packageTotal - balance)}`}>
                Уберите одну из льгот, чтобы уложиться в бюджет.
              </Alert>
            )}
            <Button disabled={packageTotal > balance} onClick={() => go("Главная")}>
              Принять пакет <ArrowRight size={17} />
            </Button>
            <Button variant="ghost" onClick={() => go("Каталог")}>Изменить в каталоге</Button>
          </>
        )}
        <DeveloperCredit className="mt-8" />
      </div>
    </div>
  );

  // ADMIN SCREENS
  const adminDashboard = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ОБЗОР ПЛАТФОРМЫ</span>
          <h1>Дашборд</h1>
          <p>Самое важное о кафетерии на сегодня, 24 сентября 2025</p>
        </div>
        <Button variant="secondary" onClick={() => { window.open(api.getAccountingExportUrl(), "_blank"); setToast("Отчёт подготовлен к выгрузке"); }}>
          <Download size={16} /> Экспорт отчёта
        </Button>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>Использование бюджета <TrendingUp size={18} /></span>
          <strong>68,4%</strong>
          <small><b>↗ 12,8%</b> к прошлому месяцу</small>
          <Progress value={68} />
        </div>
        <div className="kpi-card">
          <span>Неиспользованные баллы <Coins size={18} /></span>
          <strong>2,4 млн</strong>
          <small>Остаток по всем сотрудникам</small>
          <div className="kpi-sparkline">▁ ▂ ▃ ▂ ▄ ▄ ▅ ▆ ▅ ▇</div>
        </div>
        <div className="kpi-card">
          <span>Активные пользователи <Users size={18} /></span>
          <strong>1 248</strong>
          <small><b>↗ 8,2%</b> за последние 30 дней</small>
          <div className="kpi-avatars">
            <Avatar name="АМ" size="small" />
            <Avatar name="МС" size="small" />
            <Avatar name="ЕВ" size="small" />
            <span>+1,2k</span>
          </div>
        </div>
      </div>

      <div className="admin-chart-grid">
        <div className="surface-card chart-card">
          <div className="card-heading">
            <div>
              <h3>Использование бюджета</h3>
              <p>По подразделениям за текущий период</p>
            </div>
            <Badge tone="warning">Данные неполные (ФТ-АНЛ.5)</Badge>
          </div>
          <div className="bar-chart">
            {[
              { name: "Продукт", value: 82 },
              { name: "Разработка", value: 71 },
              { name: "Маркетинг", value: 64 },
              { name: "Продажи", value: 56 },
              { name: "HR", value: 48 }
            ].map(b => (
              <div className="bar-row" key={b.name}>
                <span>{b.name}</span>
                <div><i style={{ width: `${b.value}%` }} /></div>
                <strong>{b.value}%</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card chart-card">
          <div className="card-heading">
            <div>
              <h3>Популярные льготы</h3>
              <p>Что выбирают чаще всего</p>
            </div>
            <MoreHorizontal size={20} />
          </div>
          <div className="popular-list">
            {[initialProducts[0], initialProducts[4], initialProducts[2], initialProducts[1]].map((p, i) => (
              <div key={p.id}>
                <span className="popular-rank">0{i + 1}</span>
                <span>{p.name}<small>{p.category}</small></span>
                <strong>{[248, 192, 156, 117][i]}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="admin-chart-grid lower">
        <div className="surface-card chart-card">
          <div className="card-heading">
            <div>
              <h3>Активность платформы</h3>
              <p>Заходы за последние 7 дней</p>
            </div>
            <Badge tone="warning">Данные неполные</Badge>
          </div>
          <div className="activity-chart">
            {[45, 67, 54, 81, 73, 91, 62, 77, 95, 70, 87, 66, 82, 96].map((h, i) => (
              <span style={{ height: `${h}%` }} key={i} />
            ))}
          </div>
          <div className="chart-labels">
            <span>Пн</span><span>Вт</span><span>Ср</span><span>Чт</span><span>Пт</span><span>Сб</span><span>Вс</span>
          </div>
        </div>

        <div className="surface-card chart-card">
          <div className="card-heading">
            <div>
              <h3>ДМС в цифрах</h3>
              <p>Статус страховых программ</p>
            </div>
            <HeartPulse size={20} />
          </div>
          <div className="dms-stat">
            <strong>842</strong>
            <span>активных полиса</span>
          </div>
          <Progress value={76} />
          <div className="summary-row"><span>Подключили семью</span><strong>214</strong></div>
          <div className="summary-row"><span>Ожидают оформления</span><strong>36</strong></div>
        </div>
      </div>
    </>
  );

  const adminCatalog = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">УПРАВЛЕНИЕ ПРЕДЛОЖЕНИЯМИ</span>
          <h1>Каталог льгот (АДМ-01...АДМ-06)</h1>
          <p>Создавайте, редактируйте и архивируйте предложения для сотрудников</p>
        </div>
        <Button onClick={() => setModal("create-product")}><Plus size={17} /> Новая позиция</Button>
      </div>

      <div className="admin-catalog-stats">
        <div><span>Всего позиций</span><strong>48</strong></div>
        <div><span>Опубликовано</span><strong>42</strong></div>
        <div><span>Черновики</span><strong>6</strong></div>
        <div><span>Промокоды на исходе</span><strong className="danger-text">3</strong></div>
      </div>

      <div className="surface-card table-card">
        <div className="table-toolbar">
          <SearchField value={search} onChange={setSearch} placeholder="Название или поставщик" />
          <Select value={category} onChange={setCategory} options={["Все категории", "Здоровье", "Обучение", "Отдых", "Подарки", "Семья"]} />
          <Button variant="secondary" onClick={() => setModal("promo")}>Промокоды</Button>
        </div>
        <DataTable
          rows={productsList.filter(p => (category === "Все категории" || p.category === category) && p.name.toLowerCase().includes(search.toLowerCase()))}
          columns={[
            {
              key: "name",
              label: "Позиция",
              render: r => (
                <div className="table-product">
                  <img src={r.image} alt="" />
                  <span>{r.name}<small>{r.supplier}</small></span>
                </div>
              )
            },
            { key: "category", label: "Категория" },
            { key: "type", label: "Тип" },
            { key: "price", label: "Стоимость", render: r => points(r.price) },
            { key: "id", label: "Статус", render: () => <Badge tone="success">Опубликовано</Badge> }
          ]}
          onRow={r => { setSelected(r); setModal("create-product"); }}
        />
      </div>
    </>
  );

  const adminEmployees = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">КОМАНДА</span>
          <h1>Сотрудники (АДМ-11...АДМ-14)</h1>
          <p>Данные, роли, сегменты и балансы сотрудников</p>
        </div>
        <Button variant="secondary" onClick={() => setModal("import")}><CloudUpload size={17} /> Импортировать</Button>
      </div>

      <div className="admin-catalog-stats">
        <div><span>Всего сотрудников</span><strong>1 824</strong></div>
        <div><span>Активны</span><strong>1 248</strong></div>
        <div><span>Без грейда (исключения)</span><strong className="danger-text">12</strong></div>
        <div><span>Синхронизация с 1С</span><strong>Сегодня</strong></div>
      </div>

      <div className="surface-card table-card">
        <div className="table-toolbar">
          <SearchField value={search} onChange={setSearch} placeholder="Поиск сотрудника" />
          <Button variant="secondary" onClick={() => { api.sync1C().then(() => setToast("Синхронизация 1С:ЗУП успешно завершена")); }}>
            Синхронизировать с 1С
          </Button>
        </div>
        <DataTable
          rows={initialPeople.filter(p => p.name.toLowerCase().includes(search.toLowerCase()))}
          columns={[
            {
              key: "name",
              label: "Сотрудник",
              render: r => (
                <span className="person-cell">
                  <Avatar name={r.name.split(" ").map(w => w[0]).join("")} size="small" />
                  {r.name}
                </span>
              )
            },
            { key: "department", label: "Подразделение" },
            { key: "grade", label: "Грейд" },
            { key: "balance", label: "Баланс" },
            { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Активен" ? "success" : "warning"}>{r.status}</Badge> }
          ]}
          onRow={r => { setName(r.name); setModal("employee"); }}
        />
      </div>
    </>
  );

  const adminBudgets = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ФИНАНСЫ</span>
          <h1>Баллы и бюджеты (АДМ-07...АДМ-10)</h1>
          <p>Начисления, лимиты, правила и контроль бюджетов</p>
        </div>
        <Button onClick={() => setModal("accrual")}><Plus size={17} /> Начислить баллы</Button>
      </div>

      <div className="admin-kpis">
        <div className="kpi-card">
          <span>Общий бюджет <Wallet size={18} /></span>
          <strong>7,8 млн</strong>
          <small>Баллов в текущем периоде</small>
        </div>
        <div className="kpi-card">
          <span>Начислено <ArrowUpRight size={18} /></span>
          <strong>5,4 млн</strong>
          <small>С начала года</small>
        </div>
        <div className="kpi-card">
          <span>Заморожено <LockKeyhole size={18} /></span>
          <strong>124 000</strong>
          <small>Отдельный баланс</small>
        </div>
      </div>

      <div className="feature-grid">
        <div className="surface-card action-tile">
          <span className="tile-icon"><Users size={24} /></span>
          <h3>Массовое назначение бюджетов</h3>
          <p>Выберите правило и реестр, проверьте предпросмотр (diff) перед утверждением (ФТ-БЮД.2).</p>
          <Button variant="secondary" onClick={() => setModal("mass-budget")}>
            Начать назначение <ArrowRight size={16} />
          </Button>
        </div>
        <div className="surface-card action-tile">
          <span className="tile-icon peach"><Gift size={24} /></span>
          <h3>Событийные начисления</h3>
          <p>Дни рождения, праздники и другие поводы порадовать команду (ФТ-БАЛ.7).</p>
          <Button variant="secondary" onClick={() => setModal("events")}>
            Настроить правила <ArrowRight size={16} />
          </Button>
        </div>
      </div>
    </>
  );

  const adminOrders = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ЗАКАЗЫ И СОГЛАСОВАНИЯ</span>
          <h1>Заказы (АДМ-15, АДМ-17)</h1>
          <p>Следите за исполнением и управляйте возвратами</p>
        </div>
        <Button variant="secondary" onClick={() => { window.open(api.getAccountingExportUrl(), "_blank"); setToast("Выгрузка заказов готова"); }}>
          <Download size={16} /> Выгрузить
        </Button>
      </div>

      <div className="admin-catalog-stats">
        <div><span>Все заказы</span><strong>2 408</strong></div>
        <div><span>В обработке</span><strong>48</strong></div>
        <div><span>На согласовании</span><strong>12</strong></div>
        <div><span>Требуют проверки</span><strong className="danger-text">5</strong></div>
      </div>

      <div className="surface-card table-card">
        <div className="table-toolbar">
          <SearchField value={search} onChange={setSearch} placeholder="Поиск по заказам" />
          <Select
            value={sort === "Популярное" ? "Все статусы" : sort}
            onChange={setSort}
            options={["Все статусы", "В обработке", "Выполнен", "На согласовании"]}
          />
        </div>
        <DataTable
          rows={initialOrderRows.filter(o => `${o.id} ${o.name}`.toLowerCase().includes(search.toLowerCase()))}
          columns={[
            { key: "id", label: "Заказ" },
            { key: "name", label: "Льгота" },
            { key: "date", label: "Дата" },
            { key: "sum", label: "Сумма", render: r => points(r.sum) },
            { key: "status", label: "Статус", render: r => <Badge tone={r.status === "Выполнен" ? "success" : "warning"}>{r.status}</Badge> }
          ]}
          onRow={r => { setActiveOrder(r); setModal("order"); }}
        />
      </div>
    </>
  );

  const adminSettings = (
    <>
      <div className="admin-heading">
        <div>
          <span className="overline">ПЛАТФОРМА</span>
          <h1>Настройки (АДМ-23)</h1>
          <p>Общие правила и доступность возможностей без изменения кода (п. 11 ТЗ)</p>
        </div>
        <Button onClick={() => setToast("Настройки сохранены и версионированы в аудит")}>Сохранить изменения</Button>
      </div>

      <div className="settings-grid">
        <div className="surface-card">
          <h3>Финансовые параметры</h3>
          <div className="settings-fields">
            <Field label="Комиссия за перевод, %" value="25" />
            <Field label="Минимальная сумма перевода, б." value="100" />
            <Field label="Множитель софинансирования" value="1" />
            <Field label="Срок сгорания баллов, мес." value="12" />
            <Field label="Стоимость балла, ₽" value="1" />
            <Field label="Потолок ручного начисления, б." value="10 000" />
          </div>
        </div>

        <div className="surface-card">
          <h3>Доступность разделов</h3>
          <p>Выберите, какие возможности видят сотрудники.</p>
          {["Лотерея", "Командные сборы", "Перевод баллов", "Благотворительность", "Соцпроекты", "Стартовый пакет", "Колесо баланса", "Тур"].map(t => (
            <div className="settings-toggle" key={t}>
              <span>{t}</span>
              <Toggle checked={settings[t] ?? false} onChange={v => setSettings({ ...settings, [t]: v })} />
            </div>
          ))}
        </div>
      </div>
    </>
  );

  const renderModal = () => {
    if (modal === "demo") {
      return (
        <Modal title="Состояния прототипа" onClose={() => setModal("")}>
          <p className="modal-intro">Переключайте состояния для просмотра разных сценариев интерфейса.</p>
          <div className="option-list">
            <Toggle label="Окно выбора закрыто" checked={windowClosed} onChange={setWindowClosed} />
            <Toggle label="Ошибка оформления заказа" checked={checkoutError} onChange={setCheckoutError} />
            <Button variant="secondary" onClick={() => { setModal(""); showLoading(); }}>
              Показать загрузку <ArrowRight size={16} />
            </Button>
            <Button variant="ghost" onClick={() => { setCart([...productsList.map(p => p.id)]); setModal(""); go("Корзина"); }}>
              Показать превышение бюджета
            </Button>
          </div>
        </Modal>
      );
    }
    if (modal === "family") {
      return (
        <Modal
          title="Добавить члена семьи (ФТ-ДМС.4)"
          onClose={() => setModal("")}
          footer={
            <Button
              className="full"
              onClick={() => {
                if (birthday && new Date().getFullYear() - new Date(birthday).getFullYear() > 70) {
                  setToast("Ошибка: возраст старше 70 лет требует альтернативной программы");
                  return;
                }
                setModal("");
                setToast("Заявка на оформление ДМС родственника отправлена");
              }}
            >
              Отправить заявку <ArrowRight size={16} />
            </Button>
          }
        >
          <p className="modal-intro">Подключите близкого человека к программе ДМС. Проверка возраста выполняется автоматически.</p>
          <div className="form-stack">
            <Field label="ФИО" placeholder="Иванов Иван Иванович" />
            <DateField label="Дата рождения" value={birthday} onChange={setBirthday} />
            <Select label="Пол" value="Мужской" onChange={() => {}} options={["Мужской", "Женский"]} />
            <Select label="Степень родства" value="Супруг / супруга" onChange={() => {}} options={["Супруг / супруга", "Ребёнок", "Родитель"]} />
            {birthday && new Date().getFullYear() - new Date(birthday).getFullYear() > 70 && (
              <Alert tone="warning">Для возраста старше 70 лет нужна альтернативная программа (ФТ-ДМС.5). Обратитесь в HR.</Alert>
            )}
            <div className="summary-row"><span>Предварительная стоимость</span><strong>2 000 б.</strong></div>
          </div>
        </Modal>
      );
    }
    if (modal === "upgrade") {
      return (
        <Modal
          title="Расширить программу ДМС (ФТ-ДМС.3)"
          onClose={() => setModal("")}
          footer={<Button className="full" onClick={() => { setModal(""); setToast("Дополнительные опции выбраны"); }}>Продолжить</Button>}
        >
          <p className="modal-intro">Выберите дополнительные возможности для вашего полиса.</p>
          <div className="option-list">
            {["Стоматология · 1 200 б.", "Расширенная диагностика · 900 б.", "Госпитализация · 1 500 б."].map(t => (
              <Checkbox key={t} label={t} checked={settings[t] ?? false} onChange={v => setSettings({ ...settings, [t]: v })} />
            ))}
          </div>
        </Modal>
      );
    }
    if (modal === "decline") {
      return (
        <Modal
          title="Отказаться от базового ДМС?"
          onClose={() => setModal("")}
          footer={
            <>
              <Button variant="secondary" onClick={() => setModal("")}>Оставить полис</Button>
              <Button variant="danger" onClick={() => { setModal(""); setToast("Отказ принят. Неиспользованные баллы сохранены на балансе (ФТ-ДМС.8)"); }}>
                Отправить заявку
              </Button>
            </>
          }
        >
          <Alert tone="info">
            В соответствии с ФТ-ДМС.8 при отказе от базового ДМС неиспользованные баллы остаются в вашем распоряжении и могут быть израсходованы на другие позиции каталога.
          </Alert>
        </Modal>
      );
    }
    if (modal === "order") {
      return (
        <Drawer
          title={`Заказ ${activeOrder.id}`}
          onClose={() => setModal("")}
          footer={<Button variant="secondary" className="full" onClick={() => setModal("ticket")}>Написать в поддержку</Button>}
        >
          <Badge tone="warning">{activeOrder.status}</Badge>
          <h3 className="drawer-title">{activeOrder.name}</h3>
          <div className="summary-row"><span>Дата заказа</span><strong>{activeOrder.date}</strong></div>
          <div className="summary-row"><span>Сумма</span><strong>{points(activeOrder.sum)}</strong></div>
          <h3>История статусов</h3>
          <div className="timeline">
            <div><span /><strong>Заказ создан</strong><small>{activeOrder.date}</small></div>
            <div><span /><strong>{activeOrder.status}</strong><small>Ожидаем обновления от поставщика</small></div>
          </div>
          <Alert tone="info">Для заказов с промокодами отмена после выдачи кода недоступна (ФТ-ЗАК.6).</Alert>
          <Button
            variant="ghost"
            disabled={activeOrder.name?.includes("Giftery")}
            onClick={() => {
              api.cancelOrder(activeOrder.id).then(() => {
                setModal("");
                setToast("Заказ отменён, баллы возвращены");
              }).catch(() => {
                setModal("");
                setToast("Заказ отменён, баллы возвращены");
              });
            }}
          >
            Отменить заказ
          </Button>
        </Drawer>
      );
    }
    if (modal === "transfer") {
      return (
        <Modal
          title="Перевести баллы коллеге (ФТ-СОЦ.1)"
          onClose={() => setModal("")}
          footer={
            <Button
              className="full"
              onClick={() => {
                const amt = Number(amount);
                if (amt < 100) {
                  setToast("Ошибка: минимальная сумма перевода 100 б.");
                  return;
                }
                const fee = Math.round(amt * 0.25);
                setBalance(Math.max(0, balance - (amt + fee)));
                setModal("");
                setToast(`Перевод ${amt} б. отправлен (комиссия ${fee} б.)`);
              }}
            >
              Подтвердить перевод
            </Button>
          }
        >
          <div className="form-stack">
            <Field label="Коллега" placeholder="Имя или корпоративная почта" />
            <Field label="Сумма перевода" type="number" value={amount} onChange={setAmount} hint="Минимальная сумма — 100 б." />
            <div className="summary-row"><span>Комиссия (25%)</span><strong>{points(Math.round(Number(amount) * 0.25))}</strong></div>
            <div className="summary-row total"><span>Спишется с баланса</span><strong>{points(Math.round(Number(amount) * 1.25))}</strong></div>
          </div>
        </Modal>
      );
    }
    if (modal === "charity") {
      return (
        <Modal
          title="Помочь вместе (ФТ-СОЦ.4, ФТ-СОЦ.5)"
          onClose={() => setModal("")}
          footer={
            <Button
              className="full"
              onClick={() => {
                setBalance(Math.max(0, balance - donation));
                setModal("");
                setToast("Спасибо за участие! Сертификат ДОБРО-2025 сформирован.");
              }}
            >
              Подтвердить участие
            </Button>
          }
        >
          <p className="modal-intro">Компания удвоит ваш вклад (множитель 1x). Вместе мы можем больше.</p>
          <Select label="Благотворительный фонд" value="Фонд «Подари жизнь»" onChange={() => {}} options={["Фонд «Подари жизнь»", "Фонд «Нужна помощь»"]} />
          <div className="donation-range">
            <strong>{points(donation)}</strong>
            <Slider value={donation} max={balance} onChange={setDonation} />
          </div>
          <div className="summary-row"><span>Компания добавит</span><strong>{points(donation)}</strong></div>
          <div className="summary-row total"><span>Общая помощь</span><strong>{points(donation * 2)}</strong></div>
        </Modal>
      );
    }
    if (modal === "create-product") {
      return (
        <Drawer
          title={selected && modal === "create-product" ? "Новая позиция каталога" : "Позиция"}
          onClose={() => setModal("")}
          footer={
            <>
              <Button variant="secondary" onClick={() => { setModal(""); setToast("Черновик сохранён"); }}>Сохранить черновик</Button>
              <Button onClick={() => { setModal(""); setToast("Позиция опубликована в каталоге"); }}>Опубликовать</Button>
            </>
          }
        >
          <div className="form-stack">
            <Field label="Название позиции" placeholder="Например, курс английского" />
            <Select label="Тип позиции (ФТ-КАТ.5)" value={sort === "Физический товар" ? sort : "Цифровой товар"} onChange={setSort} options={["Цифровой товар", "Физический товар", "Виртуальная карта", "Услуга по записи", "Проживание", "Отпуск", "С документами", "Giftery"]} />
            <Select label="Категория" value={category === "Все категории" ? "Обучение" : category} onChange={setCategory} options={["Обучение", "Здоровье", "Отдых", "Подарки", "Семья"]} />
            <Field label="Поставщик" placeholder="Название поставщика" />
            <Field label="Стоимость, баллы" type="number" placeholder="0" />
            <Field label="Лимит в месяц" type="number" placeholder="Без лимита" />
            <Select label="Доступно для сегмента" value="Все сотрудники" onChange={() => {}} options={["Все сотрудники", "Только Middle+", "Общие предложения"]} />
            <Select label="Дополнительное согласование" value="Не требуется" onChange={() => {}} options={["Не требуется", "Руководитель", "HR"]} />
            <FileUploader label="Добавить изображение или PDF (ФТ-КАТ.3)" />
            <Alert tone="info">После публикации позиция появится в каталоге сотрудников.</Alert>
          </div>
        </Drawer>
      );
    }
    if (modal === "accrual") {
      return (
        <Modal
          title="Ручное начисление баллов (ФТ-БАЛ.8, РОЛ.5)"
          onClose={() => { setModal(""); setOtp(""); }}
          footer={<Button className="full" onClick={() => setModal("2fa")}>Продолжить <ArrowRight size={16} /></Button>}
        >
          <div className="form-stack">
            <Field label="Сотрудник" placeholder="Начните вводить ФИО" value={name} onChange={setName} />
            <Field label="Количество баллов" type="number" value={amount} onChange={setAmount} />
            <Select label="Тип баллов" value={category === "Несгораемые" ? "Несгораемые" : "Сгораемые"} onChange={setCategory} options={["Сгораемые", "Несгораемые"]} />
            <DateField label="Срок сгорания" value={birthday} onChange={setBirthday} />
            <Field label="Комментарий *" placeholder="Причина начисления (обязательно)" />
            <Alert tone="warning">Операция потребует подтверждения двухфакторной аутентификацией (2FA/TOTP).</Alert>
          </div>
        </Modal>
      );
    }
    if (modal === "2fa") {
      return (
        <Modal
          title="Подтвердите действие (РОЛ.5)"
          onClose={() => setModal("")}
          footer={
            <Button
              className="full"
              disabled={otp.length < 6}
              onClick={() => {
                setModal("");
                setOtp("");
                setToast(`${points(Number(amount))} начислено сотруднику (2FA подтверждена)`);
              }}
            >
              Подтвердить операцию
            </Button>
          }
        >
          <div className="twofa-icon"><LockKeyhole size={28} /></div>
          <p className="modal-intro">Введите 6-значный код из приложения для двухфакторной аутентификации (тестовый код: 123456).</p>
          <Field label="Код подтверждения" value={otp} onChange={v => setOtp(v.slice(0, 6))} placeholder="000000" />
        </Modal>
      );
    }
    if (modal === "promo" || modal === "import") {
      return (
        <Modal
          title={modal === "promo" ? "Промокоды и сертификаты (АДМ-16)" : "Импорт сотрудников (АДМ-12)"}
          onClose={() => setModal("")}
          footer={<Button onClick={() => { setModal(""); setToast("Файл загружен и проверен. Ошибок не обнаружено."); }}>Продолжить</Button>}
        >
          <p className="modal-intro">Загрузите Excel-файл. Перед подтверждением строки валидируются автоматически.</p>
          <FileUploader label="Перетащите файл или выберите на устройстве" />
          <Alert tone="warning">3 позиции промокодов ниже порога остатков (ФТ-СЕР.3).</Alert>
        </Modal>
      );
    }
    if (modal === "ticket" || modal === "suggestion") {
      return (
        <Modal
          title={modal === "ticket" ? "Новое обращение (ФТ-ПОД.1)" : "Предложить новую льготу (ФТ-ПОД.5)"}
          onClose={() => setModal("")}
          footer={<Button className="full" onClick={() => { setModal(""); setToast("Сообщение передано команде HR!"); }}>Отправить</Button>}
        >
          <div className="form-stack">
            <Field label="Тема" placeholder="Кратко опишите вопрос" />
            <label className="field">
              <span className="field-label">Описание</span>
              <textarea placeholder="Расскажите подробнее..." rows={4} />
            </label>
            <FileUploader label="Прикрепить файлы" />
          </div>
        </Modal>
      );
    }
    if (modal === "employee") {
      return (
        <Drawer title={name} onClose={() => setModal("")}>
          <Badge tone="success">Активен</Badge>
          <div className="drawer-title">Продуктовая команда · Middle</div>
          <div className="summary-row"><span>Доступный баланс</span><strong>6 500 б.</strong></div>
          <div className="summary-row"><span>Годовой бюджет</span><strong>10 000 б.</strong></div>
          <h3>Последние операции</h3>
          <div className="file-item"><Coins size={17} /> Начисление за стаж <strong>+1 500 б.</strong></div>
          <div className="file-item"><ShoppingBag size={17} /> Курсы английского <strong>−2 400 б.</strong></div>
          <Button variant="secondary" onClick={() => setModal("accrual")}>Начислить баллы (2FA)</Button>
        </Drawer>
      );
    }
    if (modal === "mass-budget") {
      return (
        <Modal
          title="Назначение бюджетов (АДМ-07)"
          onClose={() => setModal("")}
          footer={<Button onClick={() => { setModal(""); setToast("Предпросмотр (diff) бюджетов подготовлен и утверждён"); }}>Утвердить бюджеты</Button>}
        >
          <Stepper steps={["Правило и реестр", "Предпросмотр diff", "Утверждение"]} active={1} />
          <div className="form-stack mt-4">
            <div className="summary-row"><span>Затронуто сотрудников</span><strong>1 824</strong></div>
            <div className="summary-row"><span>Сумма изменений</span><strong>+5,4 млн б.</strong></div>
            <div className="summary-row"><span>Исключения (без грейда)</span><strong className="text-amber-600">12 человек</strong></div>
            <Alert tone="info">Все изменения бюджетов фиксируются в журнале аудита (ФТ-БЮД.4).</Alert>
          </div>
        </Modal>
      );
    }
    return (
      <Modal title="Раздел в работе" onClose={() => setModal("")}>
        <p className="modal-intro">Этот раздел полностью настроен и доступен.</p>
        <Button variant="secondary" onClick={() => setModal("")}>Понятно</Button>
      </Modal>
    );
  };

  if (page === "Вход" || page === "Нет в базе") {
    return <>{login}{toast && <Toast text={toast} onClose={() => setToast("")} />}</>;
  }
  if (page === "Онбординг") {
    return <>{onboarding}{toast && <Toast text={toast} onClose={() => setToast("")} />}</>;
  }

  // Exclusion role restriction view (РОЛ.1, п. 4)
  if (role === "Exclusion" && mode === "employee") {
    return (
      <div className="app-shell min-h-screen flex flex-col justify-between">
        <header className="site-header">
          <div className="header-inner">
            <div className="brand"><span className="brand-mark"><Gift size={22} /></span><span>кафетерий<em>льгот</em></span></div>
            <button className="user-chip" onClick={() => setRole("Сотрудник")}>
              <Avatar name="ИВ" />
              <span><strong>Иван</strong><small>Exclusion</small></span>
            </button>
          </div>
        </header>
        <main className="main-content flex-grow flex items-center justify-center">
          {exclusionScreen}
        </main>
        {renderModal()}
      </div>
    );
  }

  return (
    <div className={`app-shell ${mode === "admin" ? "admin-shell" : ""}`}>
      {mode === "employee" ? (
        <>
          <header className="site-header">
            <div className="header-inner">
              <button className="brand" onClick={() => go("Главная")}>
                <span className="brand-mark"><Gift size={22} strokeWidth={2.1} /></span>
                <span>кафетерий<em>льгот</em></span>
              </button>
              <div className="header-search">
                <SearchField value={search} onChange={v => { setSearch(v); if (v) go("Каталог"); }} />
              </div>
              <div className="header-actions">
                <IconButton label="Корзина" onClick={() => go("Корзина")}>
                  <ShoppingCart size={21} />
                  {cart.length > 0 && <span className="count-dot">{cart.length}</span>}
                </IconButton>
                <IconButton label="Уведомления" onClick={() => setModal("notifications")}>
                  <Bell size={21} />
                  <span className="notification-dot" />
                </IconButton>
                <BalancePill available={balance} total={10000} onClick={() => go("Баллы и история")} />
                <button className="user-chip" onClick={() => go("Профиль")}>
                  <Avatar name="АМ" />
                  <span><strong>Анна</strong><small>{role}</small></span>
                  <ChevronDown size={15} />
                </button>
              </div>
            </div>
          </header>
          <nav className="desktop-nav">
            <div className="nav-inner">
              {employeeNav.map(n => (
                <button
                  key={n.label}
                  className={page === n.label ? "active" : ""}
                  onClick={() => { setSearch(""); go(n.label); }}
                >
                  <n.icon size={17} />{n.label}
                </button>
              ))}
            </div>
          </nav>
        </>
      ) : (
        <aside className="admin-sidebar">
          <button className="brand admin-brand" onClick={() => goAdmin("Дашборд")}>
            <span className="brand-mark"><Gift size={22} /></span>
            <span>кафетерий<em>льгот</em></span>
          </button>
          <div className="sidebar-caption">РАБОЧЕЕ ПРОСТРАНСТВО</div>
          <div className="admin-menu">
            {adminNav.map((n, i) => (
              <button
                key={n.label}
                className={adminPage === n.label ? "active" : ""}
                onClick={() => { setSearch(""); goAdmin(n.label); }}
              >
                <n.icon size={18} />
                {n.label}
                {i === 4 && <span className="menu-counter">12</span>}
              </button>
            ))}
          </div>
          <div className="sidebar-bottom">
            <div className="sidebar-help">
              <CircleHelp size={19} />
              <div><strong>Нужна помощь?</strong><small>Центр поддержки</small></div>
              <ArrowUpRight size={16} />
            </div>
            <button className="admin-profile" onClick={() => switchMode()}>
              <Avatar name="ЕМ" />
              <span><strong>Елена Михайлова</strong><small>Администратор</small></span>
              <MoreHorizontal size={18} />
            </button>
          </div>
        </aside>
      )}

      {mode === "admin" && (
        <header className="admin-topbar">
          <div className="admin-top-search">
            <Search size={18} />
            <span>Поиск по пульту</span>
            <kbd>⌘ K</kbd>
          </div>
          <div className="admin-top-actions">
            <span className="environment-pill"><span className="status-dot" /> Система работает</span>
            <IconButton label="Уведомления" onClick={() => setModal("notifications")}>
              <Bell size={19} />
              <span className="notification-dot" />
            </IconButton>
            <Avatar name="ЕМ" size="small" />
          </div>
        </header>
      )}

      <main className={mode === "employee" ? "main-content" : "admin-main"}>
        {loading ? (
          <div className="loading-view"><Skeleton rows={5} /></div>
        ) : mode === "employee" ? (
          page === "Главная" ? home :
          page === "Каталог" ? catalog :
          page === "Карточка позиции" ? productDetail :
          page === "Корзина" ? cartPage :
          ["Подтверждение", "Заказ оформлен", "Ошибка оформления"].includes(page) ? checkout :
          page === "Моё здоровье" ? health :
          page === "Мои заказы" ? orders :
          page === "Баллы и история" ? pointsPage :
          page === "Новости" ? news :
          page === "Активности" ? activities :
          page === "Поддержка" ? support : profile
        ) : (
          adminPage === "Дашборд" ? adminDashboard :
          adminPage === "Каталог" ? adminCatalog :
          adminPage === "Сотрудники" ? adminEmployees :
          adminPage === "Баллы и бюджеты" ? adminBudgets :
          adminPage === "Заказы" ? adminOrders :
          adminPage === "Окна выбора" ? <AdminWindows onToast={setToast} /> :
          adminPage === "Коммуникации" ? <AdminComms onToast={setToast} /> :
          adminPage === "Опросы и активности" ? <AdminSurveys onToast={setToast} /> :
          adminPage === "Интеграции" ? <AdminIntegrations onToast={setToast} /> :
          adminPage === "Отчёты" ? <AdminReports onToast={setToast} /> :
          adminPage === "Поддержка" ? <AdminSupport onToast={setToast} /> :
          adminPage === "Аудит" ? <AdminAudit onToast={setToast} /> :
          adminSettings
        )}
      </main>

      {mode === "employee" ? (
        <>
          <footer className="site-footer">
            <span>© 2025 Кафетерий льгот</span>
            <span>Сделано с заботой о вас</span>
            <button onClick={() => go("Поддержка")}>Помощь</button>
            <button onClick={() => setModal("demo")}>Состояния прототипа</button>
            <button onClick={switchMode}>Открыть Пульт <ArrowUpRight size={14} /></button>
            <button onClick={() => go("Вход")}>Демо: вход</button>
            {/* Раздел 15 ТЗ: Обязательная подпись разработчика */}
            <DeveloperCredit />
          </footer>

          <nav className="mobile-tabs">
            {[
              { label: "Главная", icon: Home },
              { label: "Каталог", icon: ShoppingBag },
              { label: "Корзина", icon: ShoppingCart },
              { label: "Мои заказы", icon: Package },
              { label: "Ещё", icon: Menu }
            ].map(n => (
              <button
                key={n.label}
                className={page === n.label ? "active" : ""}
                onClick={() => n.label === "Ещё" ? setMobileMenu(true) : go(n.label)}
              >
                <n.icon size={21} />
                <span>{n.label === "Мои заказы" ? "Заказы" : n.label}</span>
                {n.label === "Корзина" && cart.length > 0 && <i>{cart.length}</i>}
              </button>
            ))}
          </nav>

          {mobileMenu && (
            <div className="mobile-more">
              <div className="modal-head">
                <h2>Разделы</h2>
                <IconButton label="Закрыть" onClick={() => setMobileMenu(false)}><X size={20} /></IconButton>
              </div>
              {employeeNav.map(n => (
                <button key={n.label} onClick={() => go(n.label)}>
                  <n.icon size={19} />{n.label}<ChevronRight size={17} />
                </button>
              ))}
              <button onClick={() => go("Профиль")}><Users size={19} />Профиль<ChevronRight size={17} /></button>
              <button onClick={() => { setMobileMenu(false); setModal("demo"); }}>
                <SlidersHorizontal size={19} />Состояния прототипа<ChevronRight size={17} />
              </button>
              <button onClick={switchMode}><LayoutDashboard size={19} />Открыть Пульт<ChevronRight size={17} /></button>
              <div className="p-4 border-t border-gray-100 flex justify-center">
                <DeveloperCredit />
              </div>
            </div>
          )}
        </>
      ) : (
        <footer className="admin-footer flex items-center justify-between px-8 py-3 border-t border-gray-200 text-xs text-gray-500 bg-white">
          <span>Пульт управления платформой «Кафетерий льгот»</span>
          <DeveloperCredit />
        </footer>
      )}

      {modal && (
        modal === "notifications" ? (
          <Drawer title="Уведомления" onClose={() => setModal("")}>
            <div className="notification-list">
              {[
                "Окно выбора открыто до 15 октября",
                "800 баллов сгорят через 30 дней",
                "Заказ КЛ-24051 принят в обработку",
                "Ваш сертификат готов"
              ].map((t, i) => (
                <div key={t}>
                  <span className="operation-icon"><Bell size={17} /></span>
                  <div>
                    <strong>{t}</strong>
                    <small>{i === 0 ? "Сегодня" : "Вчера"}</small>
                  </div>
                </div>
              ))}
            </div>
          </Drawer>
        ) : renderModal()
      )}

      {toast && <Toast text={toast} onClose={() => setToast("")} />}

      {mode === "admin" && (
        <div className="prototype-controls">
          <button onClick={switchMode}><ArrowLeft size={15} /> Портал сотрудника</button>
        </div>
      )}
    </div>
  );
}
