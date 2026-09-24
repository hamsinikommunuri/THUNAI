import React from 'react';
import { 
  LayoutDashboard, 
  ScanSearch, 
  CloudRain, 
  Layers, 
  CalendarRange, 
  History, 
  ShieldAlert, 
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { translations, Language } from '../i18n/translations';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  lang: Language;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, lang }) => {
  const t = translations[lang];

  const menuItems = [
    { id: 'dashboard', label: t.navDashboard, icon: LayoutDashboard, badge: null },
    { id: 'vision', label: t.navVision, icon: ScanSearch, badge: 'AI ML' },
    { id: 'weather', label: t.navWeather, icon: CloudRain, badge: 'Live' },
    { id: 'soil', label: t.navSoil, icon: Layers, badge: null },
    { id: 'planner', label: t.navPlanner, icon: CalendarRange, badge: null },
    { id: 'history', label: t.navHistory, icon: History, badge: null },
    { id: 'expert', label: t.navExpert, icon: ShieldAlert, badge: 'KVK' },
  ];

  return (
    <aside className="w-64 shrink-0 hidden lg:flex flex-col justify-between py-6 px-4 bg-[#0A0E0C] border-r border-white/[0.08] min-h-[calc(100vh-65px)]">
      <div className="space-y-6">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold px-3">
            FARM INTELLIGENCE
          </span>
          <nav className="mt-2 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-emerald text-obsidian font-bold shadow-lg shadow-emerald/15'
                      : 'text-mineral hover:bg-carbon hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-obsidian' : 'text-emerald'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded-md uppercase font-semibold ${
                      isActive ? 'bg-obsidian/20 text-obsidian' : 'bg-carbon text-emerald border border-emerald/30'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Agricultural Safety Covenant Card */}
        <div className="p-4 rounded-2xl bg-carbon/70 border border-white/5 space-y-2">
          <div className="flex items-center gap-2 text-emerald text-[11px] font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald animate-pulse"></span>
            <span>Dose Lock Covenant</span>
          </div>
          <p className="text-[11px] text-mineral-muted leading-relaxed">
            THUNAI enforces statutory pesticide bounds. We never guess chemical doses. Validated against official CIB&RC registers.
          </p>
        </div>
      </div>

      {/* Footer Info & Quick Help */}
      <div className="pt-4 border-t border-white/[0.06] space-y-2">
        <a
          href="https://agritech.tnau.ac.in"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between text-[11px] text-mineral-muted hover:text-emerald p-2 rounded-xl transition-colors"
        >
          <span>TNAU Agritech Portal</span>
          <ExternalLink className="w-3 h-3" />
        </a>
        <div className="px-2 py-1 text-[10px] font-mono text-mineral-muted/60">
          Kisan Helpline: 1800-180-1551
        </div>
      </div>
    </aside>
  );
};
