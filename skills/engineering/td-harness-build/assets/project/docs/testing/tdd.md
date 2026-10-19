# 测试驱动开发（Test-Driven Development）

> 来源与改编说明见 [tdd-NOTICE](tdd-NOTICE)，原始授权见 [tdd-LICENSE](tdd-LICENSE)。

TDD 的核心是 red → green 循环。本文是让这个循环产出“值得长期保留的测试”的参考：什么是好测试、测试写在哪里、有哪些反模式，以及循环必须遵守的规则。
进入行为改动的 Plan / Implement 阶段时按需读取本文；项目测试边界、工具和执行命令以项目测试规范及已确认 Plan 为准。

探索代码库时，如果存在 `CONTEXT.md`，先读取它，让测试名称和接口词汇与项目领域语言一致；涉及具体区域时，同时遵守该区域的 ADR（Architecture Decision Record）。

## 什么是好测试

测试应通过 public interface（公共接口）验证行为，而不是绑定 implementation details（实现细节）。代码可以大幅变化，测试不应该跟着碎掉。
好测试读起来像规格说明，例如“user can checkout with valid cart”直接说明系统具备什么能力；它能在 refactor 后继续存活，因为它不关心内部结构。

示例见[好测试与坏测试](#好测试与坏测试)，依赖隔离见[何时使用-mock](#何时使用-mock)。

## Seam：测试写在哪里

**Seam（测试接缝）**是用于测试的公共边界：你在 interface 上观察行为，而不是把手伸进内部。测试只写在 seam 上，不针对 internals（内部实现）。

在 Plan 中声明准备测试的 seam、输入、预期行为和 Mock 边界。已确认的 Plan 即为测试范围授权，Implement 内不重复请求确认；新增范围按项目工作流处理。

## 反模式

- **Implementation-coupled（绑定实现）**：仅按内部协作者的调用步骤编写断言、测试 private method，或从 side channel 验证结果，例如绕开 interface 直接查数据库。典型信号是 refactor 后行为没变，但测试坏了。
- **Tautological（同义反复）**：assertion 用与实现相同的方式重新计算 expected value，例如 `expect(add(a, b)).toBe(a + b)`、按实现步骤手算 snapshot、把常量断言成它自身。这样的测试天然成立，永远无法与代码产生真实分歧。expected value 必须来自独立事实源：已知正确 literal、完整算例或规格说明。
- **Horizontal slicing（横向切片）**：先写完所有测试，再统一写实现。批量测试验证的是想象出来的行为，测到的是形状而不是用户行为，也过早锁死测试结构。应改用 **vertical slice（纵向切片）**：一个测试 → 一个最小实现 → 重复；每个测试都是 **tracer bullet（曳光弹）**，根据上一轮学到的事实推进。

## 循环规则

- **Red before green（先红后绿）**：先写失败测试，再只写让该测试通过的最少代码。不要提前猜未来测试，也不要加入投机功能。
- **One slice at a time（一次一个切片）**：每个 cycle 只处理一个 seam、一个测试、一个最小实现。
- **Refactor（重构，可选）**：Green 后仅检查本次改动是否存在明显代码坏味道（如明显重复、过深嵌套）或违反项目明确规范。没有问题，记录“无需重构”并结束；存在问题，说明具体问题后做最小范围修正，保持行为不变、测试通过。“更优雅”或“以后可能复用”不构成重构理由。模块拆分、分层调整或新增抽象若超出已批准 Plan，须先确认；范围内修正不重复请求授权；涉及旧代码重构时，先按[验证规则](../verification.md#旧代码重构)核对方案授权及展示要求，不得为完成 TDD 阶段而扩大改动。

## 好测试与坏测试

### 好测试

**Integration-style（集成风格）**：通过被测对象的真实接口验证行为。此处描述测试风格，不要求 UT 连接真实外部服务；UT / IT 的环境边界按项目规范执行。

```typescript
// GOOD：测试可观察行为
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特征：

- 测试 users / callers 真正关心的行为
- 只使用 public API
- 能在 internal refactor 后继续通过
- 描述 WHAT，而不是 HOW
- 每个测试只有一个逻辑 assertion

### 坏测试

**Implementation-detail tests（实现细节测试）**：与 internal structure 紧耦合。

```typescript
// BAD：测试 implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

危险信号：

- Mock 内部协作者，并把实现步骤当成行为契约
- 测试 private method
- 断言不属于行为契约的 call count 或调用顺序
- refactor 后行为没变，但测试坏了
- 测试名称描述 HOW，而不是 WHAT
- 绕开 interface，通过外部 side channel 验证

```typescript
// BAD：绕过 interface 做验证
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD：通过 interface 验证
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**Tautological tests（同义反复测试）**：expected value 重复实现逻辑，因此测试天然通过。

```typescript
// BAD：expected value 按实现相同的算法重新计算
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD：expected value 是独立且已知的 literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

## 何时使用 Mock

按 Plan 声明的被测边界隔离依赖：

- 外部 API、时间、随机数及文件系统按需用 Mock / fake 隔离。
- UT 的数据库依赖使用 Mock / fake；真实测试数据库放在项目允许的 IT 中。
- 被测对象自身使用真实实现；纯函数通常直接调用。
- 函数级 UT 需要隔离的内部协作者可以 Mock，但不要仅为复现实现步骤而断言调用顺序或次数；调用本身属于契约时除外。

项目测试规范决定具体的隔离策略，本文不要求所有项目使用同一种 Mock 粒度。

### 为可 Mock 性设计

在 system boundary 上，interface 应设计得容易 mock：

**1. 使用 dependency injection（依赖注入）**

从外部传入依赖，而不是在内部直接创建：

```typescript
// 容易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难以 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. 优先使用 SDK-style interface，而不是 generic fetcher**

为每个外部操作建立具体函数，而不是用一个大而通用的函数承载条件分支：

```typescript
// GOOD：每个函数都可以独立 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD：mock 内部还需要条件分支
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK-style 方式的好处：

- 每个 mock 只返回一种明确 shape
- test setup 不需要条件分支
- 更容易看出测试覆盖了哪些 endpoint
- 每个 endpoint 都有独立 type safety
