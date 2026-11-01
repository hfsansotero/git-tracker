# git-tracker

[English](README.md) | **Español**

Una mascota en pixel art para tu perfil de GitHub que crece, cambia de color y se
mueve según tu actividad. Elige un animal o crea el tuyo a partir de una imagen.
Inspirado en [git-koi](https://github.com/yalongwastaken/git-koi).

## Cómo se refleja tu actividad

| Qué           | Sale de (por defecto)                               |
| ------------- | --------------------------------------------------- |
| **Etapa**     | Contribuciones del último año: `baby` → `young` → `adult` (umbrales 50 y 300) |
| **Animación** | Lo que pasó hasta ayer (tabla de abajo)             |
| **Colores**   | Lenguajes principales de tus repositorios públicos  |

| Animación | Cuándo (gana la primera que se cumpla)                      |
| --------- | ----------------------------------------------------------- |
| `sleep`   | 14 días o más seguidos sin contribuir                       |
| `eat`     | Ayer fue el primer día con contribuciones de su semana      |
| `active`  | Últimos 7 días al menos el doble de tu media semanal (y ≥ 5) |
| `idle`    | Cualquier otro caso                                         |

El día de hoy nunca cuenta, porque aún no ha terminado. Tanto el tamaño como la
animación pueden seguir un ritmo más lento, como tu semana o tu mes: mira
[Ajustar el ritmo](#ajustar-el-ritmo).

## En el README de tu perfil

1. Copia [examples/profile-workflow.yml](examples/profile-workflow.yml) en tu
   repositorio de perfil (`<tú>/<tú>`) como `.github/workflows/git-tracker.yml`.
2. Pon en `animal:` un animal incluido (`fox`) o una carpeta de animal de ese
   repositorio (formato abajo).
3. Añade el GIF a su `README.md`:

   ```html
   <img src="tracker/tracker.gif" alt="Mi git-tracker" />
   ```

4. Lanza el workflow una vez desde la pestaña Actions. Después se ejecuta cada noche.

| Input        | Por defecto                | Significado                                      |
| ------------ | -------------------------- | ------------------------------------------------ |
| `animal`     | (obligatorio)              | Carpeta del animal en tu repositorio, o nombre de un animal incluido |
| `login`      | El dueño del repositorio   | Cuenta cuya actividad se sigue                   |
| `output-dir` | `tracker`                  | Carpeta donde se escribe `tracker.gif`           |
| `growth`     | `year`                     | Actividad que decide el tamaño: `week`, `month` o `year` ([Ajustar el ritmo](#ajustar-el-ritmo)) |
| `mood`       | `day`                      | Actividad que decide la animación: `day`, `week` o `month` |
| `thresholds` | Depende de `growth`        | Contribuciones para pasar a young y a adult, como `5 25` |
| `token`      | El token del workflow      | Token para leer datos públicos                   |

GitHub pausa los workflows programados tras 60 días sin actividad en el
repositorio. Si pasa, vuelve a activarlo desde la pestaña Actions.

### Qué actividad y qué código se usan

- **Tus datos:** el Action lee la actividad de la cuenta dueña del repositorio
  donde se ejecuta (`login`), así que cada persona tiene su propia etapa,
  animación y colores. Nunca se mezcla la actividad de nadie más.
- **Nuestro código:** `hfsansotero/git-tracker@main` significa que cada noche usas
  la última versión de esta herramienta y de sus animales incluidos. Para
  congelar una versión, usa el SHA de un commit en lugar de `main`:
  `uses: hfsansotero/git-tracker@08c41ede109fc87551e004cc1921880de5d5df4f`.
- **Tus animales:** una carpeta de animal en tu propio repositorio es solo tuya;
  los cambios de aquí nunca la tocan.

## Ajustar el ritmo

Dos líneas en tu workflow, junto a `animal:`, eligen qué actividad sigue tu
mascota. Si no las pones, se usan los valores por defecto.

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox
          growth: month   # tamaño: tus últimos 30 días
          mood: week      # animación: tu última semana terminada
```

**`growth`, el tamaño.** Cuenta tus contribuciones en una ventana móvil y las
compara con dos umbrales: por debajo del primero, `baby`; desde el primero,
`young`; desde el segundo, `adult`. La ventana avanza cada día, así que tu mascota
crece y encoge de forma suave.

| `growth`              | Cuenta              | Umbrales por defecto (young, adult) | Cómo se siente                      |
| --------------------- | ------------------- | ----------------------------------- | ----------------------------------- |
| `week`                | Últimos 7 días      | `2 8`                               | Reacciona rápido, cambia a menudo   |
| `month`               | Últimos 30 días     | `5 25`                              | Crece a lo largo del mes; ideal con actividad ligera pero constante |
| `year` (por defecto)  | Últimos 365 días    | `50 300`                            | Muy estable, cambia despacio        |

Para poner tus propios umbrales, añade `thresholds: "<young> <adult>"`. Por
ejemplo, con `growth: month`, `thresholds: "10 60"` hace que cueste más crecer.

**`mood`, la animación.** Mira un periodo y lo compara con tu propia media, así
que tanto una cuenta tranquila como una muy activa ven todas las animaciones.

| `mood`               | Mira                                         | El GIF cambia     |
| -------------------- | -------------------------------------------- | ----------------- |
| `day` (por defecto)  | Ayer y los días anteriores                   | Cada día          |
| `week`               | Tu última semana terminada (lunes a domingo) | Los lunes         |
| `month`              | Tu último mes natural terminado              | El día 1          |

Con `week` o `month`, gana la primera regla que se cumpla:

| Animación | Cuándo                                                        |
| --------- | ------------------------------------------------------------- |
| `sleep`   | Esa semana o ese mes no tuvo contribuciones                   |
| `eat`     | Has vuelto: ese periodo tuvo contribuciones y el anterior no  |
| `active`  | Al menos el doble de tu semana o mes medio (y ≥ 5 por semana, ≥ 10 por mes) |
| `idle`    | Cualquier otro caso                                           |

Algunas combinaciones para copiar:

```yaml
# Poca actividad: verlo crecer a lo largo del mes, un estado de ánimo por semana
          growth: month
          mood: week

# Mucha actividad: cuesta llegar a adulto, la animación sigue cada día
          growth: month
          thresholds: "20 80"
          mood: day

# Tranquilo: solo cambia una vez al mes
          growth: year
          mood: month
```

Para probar una configuración antes de cambiar tu workflow, ejecuta lo mismo en
local:

```sh
git-tracker collect <tú> -o snapshot.json
git-tracker render snapshot.json animals/fox --growth month --mood week
```

Muestra la etapa, la animación y los números que hay detrás.

## Elegir tu animal

En tu perfil solo sale el animal que pongas en **tu** workflow. El resto de
animales, incluidos o tuyos, se ignoran. Para cambiarlo, edita una línea de
`.github/workflows/git-tracker.yml` en tu repositorio de perfil:

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox             # un animal incluido...
          # animal: animals/gato  # ...o una carpeta de tu repositorio de perfil
```

Para mostrar varios animales, añade un paso por animal, cada uno con su propio
`output-dir`, y un `<img>` por GIF en tu README:

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox
          output-dir: tracker/fox
      - uses: hfsansotero/git-tracker@main
        with:
          animal: animals/gato
          output-dir: tracker/gato
```

```html
<img src="tracker/fox/tracker.gif" width="192" alt="Mi zorro">
<img src="tracker/gato/tracker.gif" width="192" alt="Mi gato">
```

El paso del commit (`git add tracker`) ya recoge todas las carpetas dentro de
`tracker/`. El CI de este repositorio dibuja todos los animales incluidos solo
para probarlos; eso nunca llega al perfil de nadie.

## Animales privados

Tu repositorio de perfil tiene que ser público, así que cualquiera puede
descargar lo que haya dentro. Si quieres un animal que solo puedas usar tú
(sprites comprados, o uno que prefieres guardarte), deja sus frames en un
repositorio **privado** y deja que el workflow los descargue solo para dibujar.
El GIF de tu perfil es público, como cualquier imagen que pongas ahí, pero los
frames nunca lo son.

1. Crea un repositorio privado, como `<tú>/my-sprites`, con tu animal dentro en el
   [formato de un animal](#formato-de-un-animal), como `bat/adult/idle/01.png`.
2. Crea un [fine-grained token](https://github.com/settings/personal-access-tokens/new)
   con acceso **solo a ese repositorio** y el permiso **Contents: Read-only**.
3. En tu repositorio de perfil, abre **Settings → Secrets and variables → Actions →
   New repository secret**, llámalo `SPRITES_TOKEN` y pega el token.
4. En tu workflow, añade un paso que lo descargue antes de git-tracker y apunta
   `animal` ahí:

   ```yaml
       steps:
         - uses: actions/checkout@v4
         - uses: actions/checkout@v4
           with:
             repository: <tú>/my-sprites
             token: ${{ secrets.SPRITES_TOKEN }}
             path: private
         - uses: hfsansotero/git-tracker@main
           with:
             animal: private/bat
   ```

El paso del commit solo añade `tracker/`, así que los frames privados nunca se
suben a tu perfil. Si los sprites son comprados, comprueba que su licencia permite
mostrarlos en una web.

## Formato de un animal

Los animales incluidos y los tuyos usan el mismo formato de carpeta:

```text
animals/gato/
├── animal.json           opcional: {"fps": 6, "scale": 2, "recolor": [...]}
├── baby/                 etapa: poca actividad
│   ├── idle/             animación por defecto
│   │   ├── 01.png
│   │   └── 02.png
│   ├── active/
│   ├── eat/
│   └── sleep/
├── young/
│   └── ...
└── adult/
    └── ...
```

- **Frames:** un PNG por frame con fondo transparente, ordenados por número
  (`2.png` va antes que `10.png`).
- **Solo es obligatorio `adult/idle/01.png`.** Si falta una animación, se usa
  `idle` de la misma etapa. Si falta una etapa, se usa la más cercana (la menor si
  hay empate). Un animal puede empezar con un solo frame.
- **Tamaños:** cada etapa puede tener su propio tamaño (es como crece). Los frames
  de una animación deberían medir todos lo mismo. Cada frame se coloca centrado y
  apoyado en el borde inferior de un lienzo común a todo el animal, así el GIF
  siempre mide lo mismo.
- **Pixel art de verdad:** dibuja a tamaño real (16, 24, 32 px…) y deja que `scale`
  lo amplíe sin suavizar. No lo exportes ya ampliado.
- **`animal.json`:**
  - `fps`: velocidad de la animación, como un número o por animación:
    `{"idle": 1.5, "active": 4}` (las que falten usan 6).
  - `scale`: aumento entero del GIF.
  - `recolor`: grupos de colores exactos del sprite que toman el color de un
    lenguaje. El primer grupo toma tu lenguaje principal, el segundo el siguiente,
    y así sucesivamente: `[["#c86420", "#e07020"], ["#2040a0"], ["#5a5a5a"]]`.
    Cada píxel conserva su brillo, así que el sombreado se mantiene. Usa **tres
    grupos** (cuerpo, adornos y detalles) para que el animal muestre tus tres
    lenguajes principales; si tienes menos lenguajes, los grupos que sobran
    conservan sus colores.

## Animales incluidos

| Nombre | Cómo se hizo |
| ------ | ------------ |
| `fox`  | Poses generadas con Higgsfield y procesadas con [sources/fox/build.py](sources/fox/build.py) |

## Tu propio animal, paso a paso

1. **Instala la herramienta** para previsualizar tu animal antes de publicarlo:

   ```sh
   pip install git+https://github.com/hfsansotero/git-tracker
   ```

2. **Prepara los frames.** Elige lo que mejor te venga:
   - **Dibújalos** en un editor de pixel art (Aseprite, LibreSprite, Piskel…) y
     exporta cada frame como un PNG aparte con fondo transparente.
   - **Parte de una imagen** (un dibujo, una foto de tu mascota, una imagen
     generada con IA). Usa un PNG con fondo transparente, o con un fondo liso que
     toque las esquinas (se quita automáticamente):

     ```sh
     git-tracker pixelize foto.png animals/mio --sizes 16 24 32 --colors 16
     ```

     Crea `baby`, `young` y `adult` a 16, 24 y 32 px, cada una con un `idle`
     genérico de dos frames. Después puedes retocar o sustituir cualquier frame a
     mano.

     Si generas la imagen con IA, pide **tres zonas de color bien distintas**
     (por ejemplo: el cuerpo de un color, los adornos de otro y los detalles
     pequeños de un tercero). Cada zona será un grupo de `recolor` en el paso 5.
   - **Varias poses en una imagen** (por ejemplo, una hoja generada con IA): mira
     [sources/fox/build.py](sources/fox/build.py). Recorta la hoja, quita el fondo
     y da a todas las poses la misma escala y paleta.

3. **Ponlos en tu repositorio de perfil** siguiendo el
   [formato de un animal](#formato-de-un-animal), por ejemplo:

   ```text
   animals/mio/adult/idle/01.png
   animals/mio/adult/idle/02.png
   animals/mio/adult/sleep/01.png
   ```

   Empieza poco a poco: con `adult/idle/01.png` ya funciona. Cada animación que
   añadas se verá los días en que se cumpla su regla de
   [Cómo se refleja tu actividad](#cómo-se-refleja-tu-actividad); las que falten
   usan `idle`.

4. **Previsualízalo:**

   ```sh
   git-tracker preview animals/mio
   ```

   Genera un GIF por etapa y animación en `out/mio/`, te dice cuáles toma
   prestados de otra carpeta y lista los colores del sprite.

5. **Elige qué toma el color de tus lenguajes.** Copia colores de esa lista en
   `recolor` dentro de `animals/mio/animal.json`, junto con la velocidad y el
   tamaño:

   ```json
   {
     "fps": {"idle": 2, "active": 6, "sleep": 1, "eat": 3},
     "scale": 3,
     "recolor": [["#e26730", "#dd602d", "#c04b2b"], ["#f4e3c9", "#e8d2b0"], ["#3a2a22"]]
   }
   ```

   Un grupo por zona de color: cuerpo, adornos y detalles. Vuelve a ejecutar
   `preview`: cada color indica ahora su `recolor group`.

6. **Úsalo:** pon `animal: animals/mio` en tu workflow y haz push.

## Línea de comandos

```sh
conda create -n git-tracker python=3.13 && conda activate git-tracker
pip install -e .                              # desde un clon de este repositorio
git-tracker preview animals/gato              # un GIF por etapa y animación en out/gato/, y sus colores
export GITHUB_TOKEN=$(gh auth token)          # vale cualquier token; solo datos públicos
git-tracker collect <login> -o snapshot.json  # último año de actividad y lenguajes
git-tracker render snapshot.json animals/gato # el out/tracker.gif de hoy
```

Tests: `for f in tests/test_*.py; do python "$f"; done`

## Licencia

MIT.
