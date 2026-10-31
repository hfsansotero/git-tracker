# git-tracker

[English](README.md) | **Español**

Una mascota en pixel art para tu perfil de GitHub que crece, cambia de color y se
mueve según tu actividad. Elige un animal o crea el tuyo a partir de una imagen.
Inspirado en [git-koi](https://github.com/yalongwastaken/git-koi).

## Cómo se refleja tu actividad

| Qué           | Sale de                                             |
| ------------- | --------------------------------------------------- |
| **Etapa**     | Contribuciones del último año: `baby` → `young` → `adult` (umbrales por defecto 50 y 300) |
| **Animación** | Lo que pasó hasta ayer (tabla de abajo)             |
| **Colores**   | Lenguajes principales de tus repositorios públicos  |

| Animación | Cuándo (gana la primera que se cumpla)                      |
| --------- | ----------------------------------------------------------- |
| `sleep`   | 14 días o más seguidos sin contribuir                       |
| `eat`     | Ayer fue el primer día con contribuciones de su semana      |
| `active`  | Últimos 7 días al menos el doble de tu media semanal (y ≥ 5) |
| `idle`    | Cualquier otro caso                                         |

El crecimiento usa el último año, no todo tu historial. Así quien tiene poca
actividad también ve crecer a su mascota, y si lo dejas vuelve a encoger.

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
| `thresholds` | `50 300`                   | Contribuciones en el último año para pasar a young y a adult |
| `token`      | El token del workflow      | Token para leer datos públicos                   |

GitHub pausa los workflows programados tras 60 días sin actividad en el
repositorio. Si pasa, vuelve a activarlo desde la pestaña Actions.

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
    lenguaje. El primer grupo toma tu lenguaje principal y el segundo grupo el
    siguiente: `[["#c86420", "#e07020"], ["#2040a0"]]`. Cada píxel conserva su
    brillo, así que el sombreado se mantiene.

## Animales incluidos

| Nombre | Cómo se hizo |
| ------ | ------------ |
| `fox`  | Poses generadas con Higgsfield y procesadas con [sources/fox/build.py](sources/fox/build.py) |

## Crear un animal desde una imagen

Usa un PNG con el fondo transparente, o con un fondo liso que toque las esquinas
(se quita automáticamente):

```sh
git-tracker pixelize foto.png animals/mio --sizes 16 24 32 --colors 16
```

Crea `baby`, `young` y `adult` a 16, 24 y 32 px, cada una con un `idle` genérico de
dos frames. Después puedes retocar o sustituir cualquier frame a mano.

## Línea de comandos

```sh
conda create -n git-tracker python=3.13 && conda activate git-tracker
pip install -e .
git-tracker preview animals/gato              # un GIF por etapa y animación en out/gato/
export GITHUB_TOKEN=$(gh auth token)          # vale cualquier token; solo datos públicos
git-tracker collect <login> -o snapshot.json  # último año de actividad y lenguajes
git-tracker render snapshot.json animals/gato # el out/tracker.gif de hoy
```

Tests: `for f in tests/test_*.py; do python "$f"; done`

## Licencia

MIT.
