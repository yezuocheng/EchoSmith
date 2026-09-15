import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { BatchTaskComposer } from "./BatchTaskComposer";
import { TaskComposer } from "./TaskComposer";
import { UrlTaskComposer } from "./UrlTaskComposer";

function renderComposer(composer: JSX.Element = <BatchTaskComposer />) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      {composer}
    </QueryClientProvider>,
  );
}

describe("BatchTaskComposer transcription language", () => {
  beforeEach(() => localStorage.clear());

  it("shows English as the default transcription language", () => {
    renderComposer();

    expect(screen.getByLabelText("转写语言")).toHaveValue("en");
  });

  it("restores the previously selected transcription language", () => {
    localStorage.setItem("echosmith.transcriptionLanguage", "auto");

    renderComposer();

    expect(screen.getByLabelText("转写语言")).toHaveValue("auto");
  });

  it("persists a changed transcription language", () => {
    renderComposer();

    fireEvent.change(screen.getByLabelText("转写语言"), { target: { value: "zh" } });

    expect(localStorage.getItem("echosmith.transcriptionLanguage")).toBe("zh");
  });

  it("offers the same language choice for online transcription", () => {
    renderComposer(<UrlTaskComposer />);

    expect(screen.getByLabelText("转写语言")).toHaveValue("en");
  });

  it("offers the language choice for single-file transcription", () => {
    renderComposer(<TaskComposer />);

    expect(screen.getByLabelText("转写语言")).toHaveValue("en");
  });

  it("shows a clear start instruction after a file is dropped", () => {
    renderComposer();

    const dropZone = screen.getByRole("button", { name: /点击选择或拖拽文件到此处/ });
    const file = new File(["audio"], "lecture.wav", { type: "audio/wav" });

    fireEvent.drop(dropZone, {
      dataTransfer: { files: [file] },
    });

    expect(screen.getByText("文件已添加，请点击“开始转写”")).toBeVisible();
  });
});
