# clinica1_site — Documentação de Manutenção

Site de divulgação do sistema Clinica1, hospedado no Google Sites em **https://www.clinica1.com.br**.  
Código-fonte versionado no GitHub: **https://github.com/CesarPinheiro/clinica1_site**  
GitHub Pages (backup/espelho): **https://cesarpinheiro.github.io/clinica1_site/**

---

## Arquivos e finalidade

| Arquivo | Onde é usado | Função |
|---------|-------------|--------|
| `modulo_ia.html` | Página principal do site (embed) | Bloco CTA do Módulo IA com badge, título, pílulas de capacidades e dois botões |
| `sobre_modulo_ia.html` | Página `sobre-nosso-módulo-de-ia` (embed) | Página completa de informações do módulo IA |
| `hero.html` | Página principal (embed) | Hero / cabeçalho do site |
| `funcionalidades.html` | Página principal (embed) | Seção de funcionalidades gerais do Clinica1 |
| `como_funciona_ia.html` | Página principal (embed) | Explicação do fluxo de funcionamento da IA |

---

## Como atualizar o conteúdo

### Fluxo padrão

1. Editar o arquivo HTML localmente
2. `git add <arquivo> && git commit -m "descrição" && git push origin main`
3. No Google Sites: editar o bloco "Incorporar código" correspondente, colar o novo HTML, publicar

### Altura do embed no Google Sites

| Arquivo | Altura recomendada |
|---------|-------------------|
| `modulo_ia.html` | ~480px |
| `sobre_modulo_ia.html` | ~3000px |

---

## Estrutura de `modulo_ia.html` (bloco principal)

Bloco escuro (gradiente `#0a1628 → #0d2147 → #0a3d62`) com:
- **Badge**: "⚡ Módulo IA — Atendente Virtual via WhatsApp"
- **Título h2**: "Seu atendente virtual. Disponível 24h. Integrado ao Clinica1."
- **Descrição**: analogia com recepcionista, sem fila, sem horário
- **Pílulas de capacidades** (`.cap`): lista visual das funções do módulo
- **Botão "Sobre o módulo"**: abre `https://www.clinica1.com.br/sobre-nosso-módulo-de-ia`
- **Botão WhatsApp**: abre `https://wa.me/553190895376?text=...`

### Pílulas atuais
- 🩺 Especialidades e profissionais
- 🏥 Convênios aceitos
- 📍 Unidades de atendimento
- 📅 Agendamento e remarcação
- ❌ Cancelamento
- 🔒 Vagas exclusivas por convênio ou particular
- 👤 Reconhece pacientes recorrentes

---

## Estrutura de `sobre_modulo_ia.html` (página de informações)

Página standalone com 4 seções + header + footer:

| Seção | Label | Conteúdo |
|-------|-------|---------|
| Header | — | Gradiente escuro, título com gradient text, descrição completa |
| S1 — Vantagens | "Principais vantagens" (verde) | Grid de 9 cards com ícone emoji |
| S2 — Integração | "Integração total" (verde, fundo escuro) | 4 cards sobre integração com Clinica1 |
| S3 — Segurança | "Segurança e controle" (azul) | 5 cards com borda lateral colorida |
| S4 — Comparativo | "Comparativo" (laranja) | Tabela 11 linhas × 3 colunas |
| Footer | — | Fundo escuro, botão WhatsApp verde |

### Seção S1 — Cards de vantagens (ordem)
1. 🕐 Disponível 24h, 7 dias por semana *(destacado, fundo escuro)*
2. 🩺 Informa especialidades e profissionais
3. 📥 Desafoga a recepção
4. ⚡ Alterações on-line e em tempo real
5. 🎯 Vagas controladas pela clínica
6. 🔒 Horários exclusivos por convênio ou particular
7. 🔍 Mostra apenas o necessário
8. 👤 Reconhece pacientes recorrentes
9. 🌐 Atende em qualquer idioma

### Seção S3 — Cards de segurança (ordem)
1. 📱 Validação por telefone *(borda verde)*
2. 🔐 Acesso restrito a telefones autorizados *(borda azul)*
3. ⚙️ Controle por tipo de atendimento *(borda azul escuro)*
4. 🔒 Vagas reservadas por convênio ou particular *(borda azul)*
5. 🗃️ Histórico preservado *(borda verde)*

---

## Regras de negócio documentadas no módulo IA

- Vagas disponibilizadas ao paciente são um **subconjunto configurável** da agenda total
- Cada vaga pode ser restrita a **particular** ou a um **convênio específico** — o assistente filtra automaticamente
- O sistema exibe ao paciente **apenas o mínimo necessário** para concluir o agendamento
- Cancelamentos e remarcações só são aceitos pelo **mesmo número** que realizou o agendamento
- **Acesso restrito por telefone é opcional** — a clínica decide se aceita qualquer número ou somente números cadastrados; útil para convênios corporativos ou planos fechados
- Todos os diálogos que geraram alterações ficam **vinculados ao registro** dentro do Clinica1
- Alterações na agenda são **on-line e em tempo real** — sem importação ou lote noturno
- O assistente atende em **qualquer idioma** automaticamente

---

## Contato WhatsApp de demonstração

```
Número: 553190895376
Link agendamento: https://wa.me/553190895376?text=Ol%C3%A1%2C%20quero%20agendar%20uma%20consulta
Link atendente:   https://wa.me/553190895376?text=Ol%C3%A1%2C%20quero%20conhecer%20o%20atendente%20virtual
```

---

## Paleta de cores

| Uso | Valor |
|-----|-------|
| Fundo escuro principal | `#0a1628` / `#0d2147` / `#0a3d62` |
| Verde WhatsApp | `#25D366` |
| Azul label | `#1d4ed8` |
| Laranja label | `#c2410c` |
| Texto corpo | `#0d1b2a` |
| Texto secundário | `#64748b` |
