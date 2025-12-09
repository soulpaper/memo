# Frontend for KIS Stock Portfolio

This directory contains the Flutter frontend application.

## Prerequisites

- [Flutter SDK](https://flutter.dev/docs/get-started/install) installed on your machine.

## Getting Started

Since this project structure was generated manually, you might need to run the following command to generate the full set of platform-specific files (Android, iOS, Linux, etc.):

```bash
cd frontend
flutter create .
```

This will populate the missing directories (like `android/`, `ios/`, etc.) based on the existing `pubspec.yaml` and `lib/main.dart`.

## Running the App

1.  **Start the Backend API**:
    Make sure the FastAPI backend is running on port 8000.
    ```bash
    # From the project root
    cd API
    uvicorn main:app --reload
    ```

2.  **Run the Flutter App**:
    ```bash
    cd frontend
    flutter pub get
    flutter run -d chrome
    ```

    Note: The app is configured to connect to `http://127.0.0.1:8000/`. If you are running on a mobile emulator, you may need to adjust the URL in `lib/main.dart` (e.g., `10.0.2.2` for Android).

## Project Structure

- `lib/main.dart`: The entry point of the application. Contains the UI and logic to fetch data from the backend.
- `pubspec.yaml`: Defines the project dependencies.
- `web/index.html`: The entry point for the web application.
