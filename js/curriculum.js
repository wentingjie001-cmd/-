/*
 * 30-day core curriculum. Day 31+ is generated from this material (see session.js).
 *
 * Format per day:
 *   sounds:    [{ label, tip, ex: [[text, ipa], ...] }]
 *   pairs:     [[wordA, ipaA, wordB, ipaB]]          minimal pairs / contrasts
 *   words:     [[en, ipa, zh]]
 *   phrases:   [[en, ipa, zh]]
 *   sentences: [[en, zh]]
 *   talk:      [[question, zh, modelAnswer]]
 *
 * Placeholders resolved at build time: {name} {city} {weekday}
 * In display text, *word* marks emphasis and " / " marks a thought-group pause.
 * IPA follows the British convention used in most Chinese textbooks.
 */
(function (root) {
  const PHASES = [
    { id: 1, from: 1, to: 7, name: "Sounds → Words", zh: "第一阶段：从音标到单词", coach: "zh" },
    { id: 2, from: 8, to: 14, name: "Chunks & Phrases", zh: "第二阶段：短语块", coach: "zh" },
    { id: 3, from: 15, to: 21, name: "Simple Sentences", zh: "第三阶段：简单句子", coach: "en" },
    { id: 4, from: 22, to: 30, name: "Real Conversation", zh: "第四阶段：真实对话", coach: "en" },
    { id: 5, from: 31, to: Infinity, name: "Fluency Loop", zh: "第五阶段：流利循环", coach: "en" },
  ];

  const DAYS = [
    // ───────────── Phase 1: Sounds → Words ─────────────
    {
      title: "Hello!", zh: "打招呼", focus: "长元音 /iː/ 和短元音 /ɪ/",
      sounds: [
        { label: "/iː/", tip: "嘴角向两边拉开，像微笑，声音拉长。", ex: [["see", "siː"], ["tea", "tiː"], ["me", "miː"]] },
        { label: "/ɪ/", tip: "短而放松，嘴巴微微张开，不要拉长。", ex: [["it", "ɪt"], ["sit", "sɪt"], ["big", "bɪɡ"]] },
      ],
      pairs: [["sheep", "ʃiːp", "ship", "ʃɪp"], ["seat", "siːt", "sit", "sɪt"], ["leave", "liːv", "live", "lɪv"]],
      words: [
        ["hi", "haɪ", "嗨"], ["hello", "həˈləʊ", "你好"], ["name", "neɪm", "名字"], ["me", "miː", "我"],
        ["yes", "jes", "是的"], ["please", "pliːz", "请"], ["thanks", "θæŋks", "谢谢"], ["good", "ɡʊd", "好的"],
      ],
      phrases: [
        ["Good morning.", "ɡʊd ˈmɔːnɪŋ", "早上好"],
        ["How are you?", "haʊ ɑː juː", "你好吗？"],
        ["I'm fine.", "aɪm faɪn", "我很好"],
        ["Thank you.", "ˈθæŋk juː", "谢谢你"],
        ["Nice to meet you.", "naɪs tə miːt juː", "很高兴认识你"],
      ],
      sentences: [
        ["Hello, my name is {name}.", "你好，我叫{name}。"],
        ["I'm fine, thank you.", "我很好，谢谢。"],
        ["Nice to meet you, too.", "我也很高兴认识你。"],
        ["See you tomorrow.", "明天见。"],
      ],
      talk: [
        ["What's your name?", "你叫什么名字？", "My name is {name}."],
        ["How are you today?", "你今天好吗？", "I'm fine, thank you."],
        ["Nice to meet you.", "很高兴认识你。", "Nice to meet you, too."],
      ],
    },
    {
      title: "About Me", zh: "我来自哪里", focus: "/e/ 和 /æ/",
      sounds: [
        { label: "/e/", tip: "嘴巴半开，舌头放平，短音，像“哎”的前半。", ex: [["bed", "bed"], ["red", "red"], ["ten", "ten"]] },
        { label: "/æ/", tip: "嘴巴张大，嘴角往两边拉，介于“哎”和“啊”之间。", ex: [["cat", "kæt"], ["bag", "bæɡ"], ["man", "mæn"]] },
      ],
      pairs: [["bed", "bed", "bad", "bæd"], ["men", "men", "man", "mæn"], ["pen", "pen", "pan", "pæn"]],
      words: [
        ["China", "ˈtʃaɪnə", "中国"], ["from", "frɒm", "来自"], ["live", "lɪv", "住"], ["city", "ˈsɪti", "城市"],
        ["friend", "frend", "朋友"], ["happy", "ˈhæpi", "开心"], ["and", "ænd", "和"], ["am", "æm", "是（我是）"],
      ],
      phrases: [
        ["I'm from China.", "aɪm frəm ˈtʃaɪnə", "我来自中国"],
        ["Where are you from?", "weər ɑː juː frɒm", "你来自哪里？"],
        ["I live in {city}.", "aɪ lɪv ɪn …", "我住在{city}"],
        ["This is my friend.", "ðɪs ɪz maɪ frend", "这是我的朋友"],
        ["I'm happy.", "aɪm ˈhæpi", "我很开心"],
      ],
      sentences: [
        ["I'm from China.", "我来自中国。"],
        ["I live in a big city.", "我住在一个大城市。"],
        ["This is my friend, Tom.", "这是我的朋友，汤姆。"],
        ["Where do you live?", "你住在哪里？"],
      ],
      talk: [
        ["Where are you from?", "你来自哪里？", "I'm from China."],
        ["Where do you live?", "你住在哪里？", "I live in {city}."],
        ["Are you happy today?", "你今天开心吗？", "Yes, I'm happy."],
      ],
    },
    {
      title: "Numbers", zh: "数字", focus: "/ʌ/ 和 /ɑː/",
      sounds: [
        { label: "/ʌ/", tip: "短促，嘴巴半张，像轻轻的“阿”，不拉长。", ex: [["cup", "kʌp"], ["bus", "bʌs"], ["one", "wʌn"]] },
        { label: "/ɑː/", tip: "嘴巴张大，舌头放低靠后，声音拉长，不卷舌。", ex: [["car", "kɑː"], ["star", "stɑː"], ["father", "ˈfɑːðə"]] },
      ],
      pairs: [["cut", "kʌt", "cart", "kɑːt"], ["hut", "hʌt", "heart", "hɑːt"], ["bun", "bʌn", "barn", "bɑːn"]],
      words: [
        ["one", "wʌn", "一"], ["two", "tuː", "二"], ["three", "θriː", "三"], ["four", "fɔː", "四"], ["five", "faɪv", "五"],
        ["six", "sɪks", "六"], ["seven", "ˈsevn", "七"], ["eight", "eɪt", "八"], ["nine", "naɪn", "九"], ["ten", "ten", "十"],
      ],
      phrases: [
        ["How many?", "haʊ ˈmeni", "多少个？"],
        ["How old are you?", "haʊ əʊld ɑː juː", "你多大了？"],
        ["I'm thirty.", "aɪm ˈθɜːti", "我三十岁"],
        ["What's your number?", "wɒts jɔː ˈnʌmbə", "你的号码是多少？"],
        ["One more time, please.", "wʌn mɔː taɪm pliːz", "请再来一次"],
      ],
      sentences: [
        ["I'm twenty-five years old.", "我二十五岁。"],
        ["I have three good friends.", "我有三个好朋友。"],
        ["The bus is number five.", "公交车是五路。"],
        ["One more time, please.", "请再说一次。"],
      ],
      talk: [
        ["How old are you?", "你多大了？", "I'm twenty-five."],
        ["How many friends do you have?", "你有几个朋友？", "I have three good friends."],
        ["What's your favourite number?", "你最喜欢哪个数字？", "My favourite number is seven."],
      ],
    },
    {
      title: "Colours & Things", zh: "颜色和物品", focus: "/ɒ/ 和 /ɔː/",
      sounds: [
        { label: "/ɒ/", tip: "嘴巴张开，嘴唇略圆，短促。", ex: [["hot", "hɒt"], ["dog", "dɒɡ"], ["box", "bɒks"]] },
        { label: "/ɔː/", tip: "嘴唇收圆，声音拉长，像“奥”但更圆。", ex: [["door", "dɔː"], ["ball", "bɔːl"], ["four", "fɔː"]] },
      ],
      pairs: [["pot", "pɒt", "port", "pɔːt"], ["cod", "kɒd", "cord", "kɔːd"], ["shot", "ʃɒt", "short", "ʃɔːt"]],
      words: [
        ["red", "red", "红色"], ["blue", "bluː", "蓝色"], ["green", "ɡriːn", "绿色"], ["black", "blæk", "黑色"],
        ["white", "waɪt", "白色"], ["orange", "ˈɒrɪndʒ", "橙色"], ["phone", "fəʊn", "手机"], ["book", "bʊk", "书"],
      ],
      phrases: [
        ["What colour is it?", "wɒt ˈkʌlər ɪz ɪt", "它是什么颜色？"],
        ["It's red.", "ɪts red", "它是红色的"],
        ["I like blue.", "aɪ laɪk bluː", "我喜欢蓝色"],
        ["my phone", "maɪ fəʊn", "我的手机"],
        ["a black dog", "ə blæk dɒɡ", "一只黑狗"],
      ],
      sentences: [
        ["My phone is black.", "我的手机是黑色的。"],
        ["I like the blue one.", "我喜欢蓝色那个。"],
        ["The door is open.", "门开着。"],
        ["What's this? It's a book.", "这是什么？这是一本书。"],
      ],
      talk: [
        ["What's your favourite colour?", "你最喜欢什么颜色？", "My favourite colour is blue."],
        ["What colour is your phone?", "你的手机是什么颜色？", "My phone is black."],
        ["What's this?", "这是什么？", "It's a book."],
      ],
    },
    {
      title: "Food & Drink", zh: "吃喝", focus: "/ʊ/ 和 /uː/",
      sounds: [
        { label: "/ʊ/", tip: "嘴唇微圆，短而放松。", ex: [["good", "ɡʊd"], ["book", "bʊk"], ["put", "pʊt"]] },
        { label: "/uː/", tip: "嘴唇收圆向前突出，声音拉长，像“乌”。", ex: [["food", "fuːd"], ["two", "tuː"], ["blue", "bluː"]] },
      ],
      pairs: [["full", "fʊl", "fool", "fuːl"], ["pull", "pʊl", "pool", "puːl"], ["look", "lʊk", "Luke", "luːk"]],
      words: [
        ["water", "ˈwɔːtə", "水"], ["tea", "tiː", "茶"], ["coffee", "ˈkɒfi", "咖啡"], ["rice", "raɪs", "米饭"],
        ["noodles", "ˈnuːdlz", "面条"], ["apple", "ˈæpl", "苹果"], ["hungry", "ˈhʌŋɡri", "饿"], ["cook", "kʊk", "做饭"],
      ],
      phrases: [
        ["I'm hungry.", "aɪm ˈhʌŋɡri", "我饿了"],
        ["a cup of tea", "ə kʌp əv tiː", "一杯茶"],
        ["Can I have some water?", "kən aɪ hæv səm ˈwɔːtə", "可以给我点水吗？"],
        ["It's good.", "ɪts ɡʊd", "很好吃"],
        ["I'd like some rice.", "aɪd laɪk səm raɪs", "我想要点米饭"],
      ],
      sentences: [
        ["I'm hungry. Let's eat.", "我饿了，我们吃饭吧。"],
        ["Can I have a cup of tea, please?", "请给我一杯茶，好吗？"],
        ["I like noodles.", "我喜欢面条。"],
        ["This food is good.", "这个菜很好吃。"],
      ],
      talk: [
        ["Do you like coffee?", "你喜欢咖啡吗？", "Yes, I like coffee."],
        ["What do you eat for breakfast?", "你早餐吃什么？", "I eat noodles for breakfast."],
        ["Are you hungry?", "你饿了吗？", "Yes, I'm a little hungry."],
      ],
    },
    {
      title: "My Family", zh: "我的家人", focus: "/ɜː/ 和 /ə/",
      sounds: [
        { label: "/ɜː/", tip: "嘴巴半开，舌头放在中间，拉长，不卷舌。", ex: [["bird", "bɜːd"], ["work", "wɜːk"], ["girl", "ɡɜːl"]] },
        { label: "/ə/", tip: "最轻最短的音，嘴巴完全放松，一带而过。", ex: [["a", "ə"], ["sofa", "ˈsəʊfə"], ["mother", "ˈmʌðə"]] },
      ],
      pairs: [["bird", "bɜːd", "bud", "bʌd"], ["hurt", "hɜːt", "hut", "hʌt"], ["firm", "fɜːm", "farm", "fɑːm"]],
      words: [
        ["mother", "ˈmʌðə", "妈妈"], ["father", "ˈfɑːðə", "爸爸"], ["sister", "ˈsɪstə", "姐妹"], ["brother", "ˈbrʌðə", "兄弟"],
        ["son", "sʌn", "儿子"], ["daughter", "ˈdɔːtə", "女儿"], ["wife", "waɪf", "妻子"], ["husband", "ˈhʌzbənd", "丈夫"],
      ],
      phrases: [
        ["my family", "maɪ ˈfæməli", "我的家人"],
        ["This is my mother.", "ðɪs ɪz maɪ ˈmʌðə", "这是我妈妈"],
        ["I have a sister.", "aɪ hæv ə ˈsɪstə", "我有一个姐姐"],
        ["How many people?", "haʊ ˈmeni ˈpiːpl", "多少人？"],
        ["my little brother", "maɪ ˈlɪtl ˈbrʌðə", "我的弟弟"],
      ],
      sentences: [
        ["There are four people in my family.", "我家有四口人。"],
        ["My mother is a teacher.", "我妈妈是老师。"],
        ["I have one brother and one sister.", "我有一个兄弟和一个姐妹。"],
        ["I love my family.", "我爱我的家人。"],
      ],
      talk: [
        ["How many people are in your family?", "你家有几口人？", "There are four people in my family."],
        ["Do you have a brother or a sister?", "你有兄弟姐妹吗？", "I have one sister."],
        ["What does your mother do?", "你妈妈做什么工作？", "My mother is a teacher."],
      ],
    },
    {
      title: "Days of the Week", zh: "星期 + 第一周复习", focus: "咬舌音 /θ/ 和 /ð/",
      sounds: [
        { label: "/θ/", tip: "舌尖轻轻放在上下牙之间，往外吹气，声带不振动。", ex: [["three", "θriː"], ["think", "θɪŋk"], ["thanks", "θæŋks"]] },
        { label: "/ð/", tip: "舌头位置一样，但声带振动，喉咙有嗡嗡感。", ex: [["this", "ðɪs"], ["that", "ðæt"], ["mother", "ˈmʌðə"]] },
      ],
      pairs: [["think", "θɪŋk", "sink", "sɪŋk"], ["three", "θriː", "tree", "triː"], ["they", "ðeɪ", "day", "deɪ"]],
      words: [
        ["Monday", "ˈmʌndeɪ", "星期一"], ["Tuesday", "ˈtjuːzdeɪ", "星期二"], ["Wednesday", "ˈwenzdeɪ", "星期三"],
        ["Thursday", "ˈθɜːzdeɪ", "星期四"], ["Friday", "ˈfraɪdeɪ", "星期五"], ["Saturday", "ˈsætədeɪ", "星期六"],
        ["Sunday", "ˈsʌndeɪ", "星期日"], ["today", "təˈdeɪ", "今天"],
      ],
      phrases: [
        ["Thank you very much.", "ˈθæŋk juː ˈveri mʌtʃ", "非常感谢"],
        ["What day is it today?", "wɒt deɪ ɪz ɪt təˈdeɪ", "今天星期几？"],
        ["See you on Monday.", "siː juː ɒn ˈmʌndeɪ", "星期一见"],
        ["this weekend", "ðɪs ˌwiːkˈend", "这个周末"],
        ["I think so.", "aɪ θɪŋk səʊ", "我想是的"],
      ],
      sentences: [
        ["Today is {weekday}.", "今天是{weekdayZh}。"],
        ["I think it's Friday.", "我觉得是星期五。"],
        ["Thank you for your help.", "谢谢你的帮助。"],
        ["See you this weekend.", "周末见。"],
      ],
      talk: [
        ["What day is it today?", "今天星期几？", "Today is {weekday}."],
        ["What do you do on Sunday?", "你星期天做什么？", "On Sunday, I rest at home."],
        ["Tell me your name and where you're from.", "说说你的名字和你来自哪里。", "My name is {name}. I'm from China."],
      ],
    },

    // ───────────── Phase 2: Chunks & Phrases ─────────────
    {
      title: "Daily Routine", zh: "一天的作息", focus: "/v/ 和 /w/",
      sounds: [
        { label: "/v/", tip: "上牙轻轻碰下嘴唇，声带振动。", ex: [["very", "ˈveri"], ["five", "faɪv"], ["live", "lɪv"]] },
        { label: "/w/", tip: "双唇先收圆再张开，牙齿不碰嘴唇。", ex: [["we", "wiː"], ["water", "ˈwɔːtə"], ["work", "wɜːk"]] },
      ],
      pairs: [["vest", "vest", "west", "west"], ["vine", "vaɪn", "wine", "waɪn"], ["vet", "vet", "wet", "wet"]],
      words: [
        ["morning", "ˈmɔːnɪŋ", "早上"], ["evening", "ˈiːvnɪŋ", "晚上"], ["work", "wɜːk", "工作"], ["breakfast", "ˈbrekfəst", "早餐"],
        ["shower", "ˈʃaʊə", "淋浴"], ["sleep", "sliːp", "睡觉"], ["every", "ˈevri", "每一个"], ["usually", "ˈjuːʒuəli", "通常"],
      ],
      phrases: [
        ["I get up at seven.", "aɪ ɡet ʌp ət ˈsevn", "我七点起床"],
        ["have breakfast", "hæv ˈbrekfəst", "吃早餐"],
        ["go to work", "ɡəʊ tə wɜːk", "去上班"],
        ["every day", "ˈevri deɪ", "每天"],
        ["go to bed", "ɡəʊ tə bed", "上床睡觉"],
      ],
      sentences: [
        ["I get up at seven every day.", "我每天七点起床。"],
        ["I have breakfast at home.", "我在家吃早餐。"],
        ["I go to work by bus.", "我坐公交车上班。"],
        ["I usually go to bed at eleven.", "我通常十一点睡觉。"],
      ],
      talk: [
        ["What time do you get up?", "你几点起床？", "I get up at seven."],
        ["How do you go to work?", "你怎么去上班？", "I go to work by bus."],
        ["What do you do in the evening?", "你晚上做什么？", "In the evening, I watch TV."],
      ],
    },
    {
      title: "Time", zh: "时间", focus: "/l/ 和 /n/",
      sounds: [
        { label: "/l/", tip: "舌尖顶住上牙后面的牙龈，声音从舌头两边出来。", ex: [["light", "laɪt"], ["like", "laɪk"], ["hello", "həˈləʊ"]] },
        { label: "/n/", tip: "舌尖同样顶住牙龈，但声音从鼻子出来。", ex: [["no", "nəʊ"], ["night", "naɪt"], ["nine", "naɪn"]] },
      ],
      pairs: [["light", "laɪt", "night", "naɪt"], ["low", "ləʊ", "no", "nəʊ"], ["lap", "læp", "nap", "næp"]],
      words: [
        ["o'clock", "əˈklɒk", "点钟"], ["half", "hɑːf", "一半"], ["quarter", "ˈkwɔːtə", "一刻钟"], ["minute", "ˈmɪnɪt", "分钟"],
        ["hour", "ˈaʊə", "小时"], ["late", "leɪt", "晚的"], ["early", "ˈɜːli", "早的"], ["now", "naʊ", "现在"],
      ],
      phrases: [
        ["What time is it?", "wɒt taɪm ɪz ɪt", "几点了？"],
        ["It's nine o'clock.", "ɪts naɪn əˈklɒk", "九点了"],
        ["half past seven", "hɑːf pɑːst ˈsevn", "七点半"],
        ["Sorry, I'm late.", "ˈsɒri aɪm leɪt", "对不起，我迟到了"],
        ["in ten minutes", "ɪn ten ˈmɪnɪts", "十分钟后"],
      ],
      sentences: [
        ["It's half past nine.", "现在九点半。"],
        ["Sorry, I'm late.", "对不起，我迟到了。"],
        ["The class starts in ten minutes.", "课十分钟后开始。"],
        ["I don't like to get up early.", "我不喜欢早起。"],
      ],
      talk: [
        ["What time is it now?", "现在几点了？", "It's ten o'clock."],
        ["Do you get up early?", "你起得早吗？", "Yes, I get up early."],
        ["When do you have lunch?", "你什么时候吃午饭？", "I have lunch at twelve."],
      ],
    },
    {
      title: "Shopping", zh: "购物", focus: "/r/ 和 /l/",
      sounds: [
        { label: "/r/", tip: "舌尖向上卷起但不碰上颚，嘴唇微圆。", ex: [["red", "red"], ["right", "raɪt"], ["sorry", "ˈsɒri"]] },
        { label: "/l/", tip: "舌尖顶住上牙龈，再放开。", ex: [["look", "lʊk"], ["light", "laɪt"], ["love", "lʌv"]] },
      ],
      pairs: [["right", "raɪt", "light", "laɪt"], ["rice", "raɪs", "lice", "laɪs"], ["read", "riːd", "lead", "liːd"]],
      words: [
        ["money", "ˈmʌni", "钱"], ["price", "praɪs", "价格"], ["cheap", "tʃiːp", "便宜"], ["expensive", "ɪkˈspensɪv", "贵"],
        ["buy", "baɪ", "买"], ["shop", "ʃɒp", "商店"], ["size", "saɪz", "尺码"], ["card", "kɑːd", "卡"],
      ],
      phrases: [
        ["How much is it?", "haʊ mʌtʃ ɪz ɪt", "多少钱？"],
        ["It's too expensive.", "ɪts tuː ɪkˈspensɪv", "太贵了"],
        ["Can I pay by card?", "kən aɪ peɪ baɪ kɑːd", "可以刷卡吗？"],
        ["I'm just looking.", "aɪm dʒʌst ˈlʊkɪŋ", "我只是看看"],
        ["I'll take it.", "aɪl teɪk ɪt", "我买了"],
      ],
      sentences: [
        ["How much is this shirt?", "这件衬衫多少钱？"],
        ["It's too expensive for me.", "对我来说太贵了。"],
        ["Do you have a smaller size?", "有小一点的尺码吗？"],
        ["I'll take it, thank you.", "我买了，谢谢。"],
      ],
      talk: [
        ["Hello! Can I help you?", "（店员）你好！需要帮忙吗？", "I'm just looking, thanks."],
        ["This one is fifty dollars.", "（店员）这个五十美元。", "That's too expensive for me."],
        ["How would you like to pay?", "（店员）你想怎么付款？", "Can I pay by card?"],
      ],
    },
    {
      title: "Likes & Dislikes", zh: "喜欢和不喜欢", focus: "双元音 /eɪ/ 和 /aɪ/",
      sounds: [
        { label: "/eɪ/", tip: "从 /e/ 滑到 /ɪ/，像“诶”，要有滑动感。", ex: [["day", "deɪ"], ["name", "neɪm"], ["play", "pleɪ"]] },
        { label: "/aɪ/", tip: "从 /a/ 滑到 /ɪ/，嘴巴先张大，像“爱”。", ex: [["my", "maɪ"], ["like", "laɪk"], ["time", "taɪm"]] },
      ],
      pairs: [["late", "leɪt", "light", "laɪt"], ["main", "meɪn", "mine", "maɪn"], ["may", "meɪ", "my", "maɪ"]],
      words: [
        ["like", "laɪk", "喜欢"], ["love", "lʌv", "热爱"], ["hate", "heɪt", "讨厌"], ["music", "ˈmjuːzɪk", "音乐"],
        ["movie", "ˈmuːvi", "电影"], ["game", "ɡeɪm", "游戏"], ["sport", "spɔːt", "运动"], ["really", "ˈrɪəli", "真的"],
      ],
      phrases: [
        ["I really like it.", "aɪ ˈrɪəli laɪk ɪt", "我真的很喜欢"],
        ["I don't like it.", "aɪ dəʊnt laɪk ɪt", "我不喜欢"],
        ["What do you like?", "wɒt də juː laɪk", "你喜欢什么？"],
        ["play games", "pleɪ ɡeɪmz", "玩游戏"],
        ["Me too.", "miː tuː", "我也是"],
      ],
      sentences: [
        ["I really like music.", "我真的很喜欢音乐。"],
        ["I don't like sports very much.", "我不太喜欢运动。"],
        ["I love watching movies.", "我很爱看电影。"],
        ["What kind of music do you like?", "你喜欢哪种音乐？"],
      ],
      talk: [
        ["What do you like to do?", "你喜欢做什么？", "I like to play games."],
        ["Do you like sports?", "你喜欢运动吗？", "Not really. I like music."],
        ["What's your favourite food?", "你最喜欢的食物是什么？", "My favourite food is noodles."],
      ],
    },
    {
      title: "Directions", zh: "问路", focus: "双元音 /əʊ/ 和 /aʊ/",
      sounds: [
        { label: "/əʊ/", tip: "从 /ə/ 滑到 /ʊ/，嘴唇慢慢收圆，像“欧”。", ex: [["go", "ɡəʊ"], ["no", "nəʊ"], ["home", "həʊm"]] },
        { label: "/aʊ/", tip: "从 /a/ 滑到 /ʊ/，嘴巴先张大，像“傲”。", ex: [["now", "naʊ"], ["how", "haʊ"], ["town", "taʊn"]] },
      ],
      pairs: [["no", "nəʊ", "now", "naʊ"], ["tone", "təʊn", "town", "taʊn"], ["load", "ləʊd", "loud", "laʊd"]],
      words: [
        ["left", "left", "左"], ["right", "raɪt", "右"], ["straight", "streɪt", "直走"], ["near", "nɪə", "近"],
        ["far", "fɑː", "远"], ["station", "ˈsteɪʃn", "车站"], ["road", "rəʊd", "路"], ["hospital", "ˈhɒspɪtl", "医院"],
      ],
      phrases: [
        ["Excuse me.", "ɪkˈskjuːz miː", "打扰一下"],
        ["Where is the station?", "weər ɪz ðə ˈsteɪʃn", "车站在哪里？"],
        ["Go straight.", "ɡəʊ streɪt", "直走"],
        ["Turn left.", "tɜːn left", "左转"],
        ["It's near here.", "ɪts nɪə hɪə", "就在附近"],
      ],
      sentences: [
        ["Excuse me, where is the station?", "打扰一下，车站在哪里？"],
        ["Go straight and turn left.", "直走，然后左转。"],
        ["It's not far from here.", "离这里不远。"],
        ["The hospital is on the right.", "医院在右边。"],
      ],
      talk: [
        ["Excuse me, is there a bank near here?", "打扰一下，附近有银行吗？", "Yes, go straight and turn right."],
        ["How do I get to the station?", "我怎么去车站？", "Turn left, then go straight."],
        ["Is it far?", "远吗？", "No, it's very near."],
      ],
    },
    {
      title: "Weather", zh: "天气", focus: "双元音 /ɪə/ /eə/ /ʊə/",
      sounds: [
        { label: "/ɪə/", tip: "从 /ɪ/ 滑到 /ə/。", ex: [["here", "hɪə"], ["near", "nɪə"], ["ear", "ɪə"]] },
        { label: "/eə/", tip: "从 /e/ 滑到 /ə/，嘴巴比 /ɪə/ 张得大。", ex: [["hair", "heə"], ["where", "weə"], ["chair", "tʃeə"]] },
        { label: "/ʊə/", tip: "从 /ʊ/ 滑到 /ə/，嘴唇先圆后松。", ex: [["tour", "tʊə"], ["poor", "pʊə"], ["sure", "ʃʊə"]] },
      ],
      pairs: [["here", "hɪə", "hair", "heə"], ["ear", "ɪə", "air", "eə"], ["beer", "bɪə", "bear", "beə"]],
      words: [
        ["weather", "ˈweðə", "天气"], ["sunny", "ˈsʌni", "晴朗"], ["rainy", "ˈreɪni", "下雨的"], ["cold", "kəʊld", "冷"],
        ["hot", "hɒt", "热"], ["windy", "ˈwɪndi", "有风的"], ["cloudy", "ˈklaʊdi", "多云的"], ["warm", "wɔːm", "暖和"],
      ],
      phrases: [
        ["It's sunny today.", "ɪts ˈsʌni təˈdeɪ", "今天是晴天"],
        ["It's very cold.", "ɪts ˈveri kəʊld", "很冷"],
        ["What's the weather like?", "wɒts ðə ˈweðə laɪk", "天气怎么样？"],
        ["I think it'll rain.", "aɪ θɪŋk ˈɪtl reɪn", "我觉得会下雨"],
        ["Take an umbrella.", "teɪk ən ʌmˈbrelə", "带把伞"],
      ],
      sentences: [
        ["What's the weather like today?", "今天天气怎么样？"],
        ["It's cold and windy outside.", "外面又冷又有风。"],
        ["I like sunny days.", "我喜欢晴天。"],
        ["Take an umbrella. It's going to rain.", "带把伞，要下雨了。"],
      ],
      talk: [
        ["What's the weather like today?", "今天天气怎么样？", "It's sunny and warm."],
        ["Do you like hot weather?", "你喜欢热天吗？", "No, I like cool weather."],
        ["What's your favourite season?", "你最喜欢哪个季节？", "My favourite season is autumn."],
      ],
    },
    {
      title: "At a Restaurant", zh: "在餐厅 + 第二周复习", focus: "词尾辅音不加“额”",
      sounds: [
        { label: "词尾 /t/ /d/", tip: "词尾辅音轻轻收住，不要加“额”：good 不说成 goo-de。", ex: [["good", "ɡʊd"], ["eight", "eɪt"], ["red", "red"]] },
        { label: "词尾 /k/ /ɡ/", tip: "舌根顶住后收住，不要加“额”：book 不说成 boo-ke。", ex: [["book", "bʊk"], ["big", "bɪɡ"], ["like", "laɪk"]] },
      ],
      pairs: [["bay", "beɪ", "bake", "beɪk"], ["tie", "taɪ", "tide", "taɪd"], ["see", "siː", "seat", "siːt"]],
      words: [
        ["menu", "ˈmenjuː", "菜单"], ["order", "ˈɔːdə", "点菜"], ["table", "ˈteɪbl", "桌子"], ["bill", "bɪl", "账单"],
        ["delicious", "dɪˈlɪʃəs", "美味的"], ["spicy", "ˈspaɪsi", "辣的"], ["chicken", "ˈtʃɪkɪn", "鸡肉"], ["beef", "biːf", "牛肉"],
      ],
      phrases: [
        ["A table for two, please.", "ə ˈteɪbl fə tuː pliːz", "两位，谢谢"],
        ["Can I see the menu?", "kən aɪ siː ðə ˈmenjuː", "能看看菜单吗？"],
        ["I'd like the chicken.", "aɪd laɪk ðə ˈtʃɪkɪn", "我要鸡肉"],
        ["It's delicious.", "ɪts dɪˈlɪʃəs", "很好吃"],
        ["Can I have the bill?", "kən aɪ hæv ðə bɪl", "可以买单吗？"],
      ],
      sentences: [
        ["A table for two, please.", "两位，谢谢。"],
        ["I'd like the chicken and rice.", "我要鸡肉饭。"],
        ["Not too spicy, please.", "请不要太辣。"],
        ["Excuse me, can I have the bill?", "打扰一下，可以买单吗？"],
      ],
      talk: [
        ["Are you ready to order?", "（服务员）可以点菜了吗？", "Yes, I'd like the beef noodles."],
        ["Anything to drink?", "（服务员）喝点什么？", "A cup of tea, please."],
        ["How is your food?", "（服务员）菜怎么样？", "It's delicious, thank you."],
      ],
    },

    // ───────────── Phase 3: Simple Sentences ─────────────
    {
      title: "My Job", zh: "工作（一般现在时）", focus: "/ʃ/ /tʃ/ /dʒ/",
      sounds: [
        { label: "/ʃ/", tip: "嘴唇向前突出，送气，像“嘘”。", ex: [["she", "ʃiː"], ["shop", "ʃɒp"], ["fish", "fɪʃ"]] },
        { label: "/tʃ/", tip: "先堵住再突然放开，嘴唇突出，像“吃”。", ex: [["chair", "tʃeə"], ["much", "mʌtʃ"], ["teacher", "ˈtiːtʃə"]] },
        { label: "/dʒ/", tip: "和 /tʃ/ 一样，但声带振动，像“just”的开头。", ex: [["job", "dʒɒb"], ["age", "eɪdʒ"], ["orange", "ˈɒrɪndʒ"]] },
      ],
      pairs: [["ship", "ʃɪp", "chip", "tʃɪp"], ["shoes", "ʃuːz", "choose", "tʃuːz"], ["cheap", "tʃiːp", "jeep", "dʒiːp"]],
      words: [
        ["job", "dʒɒb", "工作"], ["teacher", "ˈtiːtʃə", "老师"], ["office", "ˈɒfɪs", "办公室"], ["company", "ˈkʌmpəni", "公司"],
        ["busy", "ˈbɪzi", "忙"], ["meeting", "ˈmiːtɪŋ", "会议"], ["boss", "bɒs", "老板"], ["colleague", "ˈkɒliːɡ", "同事"],
      ],
      phrases: [
        ["What do you do?", "wɒt də juː duː", "你是做什么的？"],
        ["I work in an office.", "aɪ wɜːk ɪn ən ˈɒfɪs", "我在办公室工作"],
        ["I'm very busy.", "aɪm ˈveri ˈbɪzi", "我很忙"],
        ["She is a teacher.", "ʃiː ɪz ə ˈtiːtʃə", "她是老师"],
        ["I have a meeting.", "aɪ hæv ə ˈmiːtɪŋ", "我有个会"],
      ],
      sentences: [
        ["I work in an office in the city.", "我在市里的一个办公室工作。"],
        ["She teaches English at a school.", "她在一所学校教英语。"],
        ["My job is very busy.", "我的工作很忙。"],
        ["I have a meeting every Monday.", "我每周一都有会。"],
      ],
      talk: [
        ["What do you do?", "你是做什么工作的？", "I work in an office."],
        ["Do you like your job?", "你喜欢你的工作吗？", "Yes, I like my job, but it's busy."],
        ["What time do you finish work?", "你几点下班？", "I finish work at six."],
      ],
    },
    {
      title: "He Likes, She Goes", zh: "他/她（第三人称 -s）", focus: "词尾 -s：/s/ /z/ /ɪz/",
      sounds: [
        { label: "-s 读 /s/", tip: "清辅音（p t k f）后面，-s 读 /s/，只送气。", ex: [["books", "bʊks"], ["works", "wɜːks"], ["cats", "kæts"]] },
        { label: "-s 读 /z/", tip: "浊音和元音后面，-s 读 /z/，喉咙振动。", ex: [["dogs", "dɒɡz"], ["plays", "pleɪz"], ["lives", "lɪvz"]] },
        { label: "-es 读 /ɪz/", tip: "s、sh、ch 后面，多一个音节 /ɪz/。", ex: [["watches", "ˈwɒtʃɪz"], ["buses", "ˈbʌsɪz"], ["washes", "ˈwɒʃɪz"]] },
      ],
      pairs: [["price", "praɪs", "prize", "praɪz"], ["bus", "bʌs", "buzz", "bʌz"], ["place", "pleɪs", "plays", "pleɪz"]],
      words: [
        ["he", "hiː", "他"], ["she", "ʃiː", "她"], ["likes", "laɪks", "喜欢（他/她）"], ["plays", "pleɪz", "玩（他/她）"],
        ["watches", "ˈwɒtʃɪz", "看（他/她）"], ["goes", "ɡəʊz", "去（他/她）"], ["has", "hæz", "有（他/她）"], ["does", "dʌz", "做（他/她）"],
      ],
      phrases: [
        ["He likes football.", "hiː laɪks ˈfʊtbɔːl", "他喜欢足球"],
        ["She goes to school.", "ʃiː ɡəʊz tə skuːl", "她去上学"],
        ["He has a car.", "hiː hæz ə kɑː", "他有一辆车"],
        ["She watches TV.", "ʃiː ˈwɒtʃɪz ˌtiːˈviː", "她看电视"],
        ["Does he know?", "dʌz hiː nəʊ", "他知道吗？"],
      ],
      sentences: [
        ["My brother likes football.", "我哥哥喜欢足球。"],
        ["She goes to work by car.", "她开车上班。"],
        ["He watches TV every night.", "他每晚看电视。"],
        ["Does your friend speak English?", "你的朋友说英语吗？"],
      ],
      talk: [
        ["Tell me about your friend. What does your friend do?", "说说你的朋友，他/她做什么工作？", "My friend works in a bank."],
        ["What does your mother like?", "你妈妈喜欢什么？", "She likes cooking."],
        ["Does your friend speak English?", "你的朋友说英语吗？", "Yes, she speaks English very well."],
      ],
    },
    {
      title: "Yesterday", zh: "昨天（一般过去时）", focus: "词尾 -ed：/t/ /d/ /ɪd/",
      sounds: [
        { label: "-ed 读 /t/", tip: "清辅音后面，-ed 读 /t/，短促收住。", ex: [["worked", "wɜːkt"], ["walked", "wɔːkt"], ["watched", "wɒtʃt"]] },
        { label: "-ed 读 /d/", tip: "浊音和元音后面，-ed 读 /d/。", ex: [["played", "pleɪd"], ["lived", "lɪvd"], ["cleaned", "kliːnd"]] },
        { label: "-ed 读 /ɪd/", tip: "t 和 d 后面，多一个音节 /ɪd/。", ex: [["wanted", "ˈwɒntɪd"], ["needed", "ˈniːdɪd"], ["visited", "ˈvɪzɪtɪd"]] },
      ],
      pairs: [["play", "pleɪ", "played", "pleɪd"], ["walk", "wɔːk", "walked", "wɔːkt"], ["want", "wɒnt", "wanted", "ˈwɒntɪd"]],
      words: [
        ["yesterday", "ˈjestədeɪ", "昨天"], ["last", "lɑːst", "上一个"], ["went", "went", "去了"], ["ate", "eɪt", "吃了"],
        ["saw", "sɔː", "看见了"], ["had", "hæd", "有过/吃过"], ["was", "wɒz", "是（过去）"], ["did", "dɪd", "做了"],
      ],
      phrases: [
        ["last night", "lɑːst naɪt", "昨晚"],
        ["I went home.", "aɪ went həʊm", "我回家了"],
        ["I watched a movie.", "aɪ wɒtʃt ə ˈmuːvi", "我看了一部电影"],
        ["It was great.", "ɪt wəz ɡreɪt", "很棒"],
        ["What did you do?", "wɒt dɪd juː duː", "你做了什么？"],
      ],
      sentences: [
        ["Yesterday I worked from nine to six.", "昨天我从九点工作到六点。"],
        ["Last night I watched a movie at home.", "昨晚我在家看了部电影。"],
        ["I went to the park on Sunday.", "我星期天去了公园。"],
        ["It was a good day.", "那是美好的一天。"],
      ],
      talk: [
        ["What did you do yesterday?", "你昨天做了什么？", "Yesterday I worked, and then I cooked dinner."],
        ["What did you eat last night?", "你昨晚吃了什么？", "I ate rice and chicken."],
        ["How was your weekend?", "你周末过得怎么样？", "It was great. I visited my parents."],
      ],
    },
    {
      title: "Plans", zh: "计划（be going to）", focus: "辅音连缀，中间不加元音",
      sounds: [
        { label: "/st/ /str/", tip: "辅音直接连在一起：street 不说成 si-te-reet。", ex: [["stop", "stɒp"], ["street", "striːt"], ["strong", "strɒŋ"]] },
        { label: "/pl/ /pr/ /bl/", tip: "两个辅音一口气连读。", ex: [["play", "pleɪ"], ["price", "praɪs"], ["blue", "bluː"]] },
        { label: "/ks/ /kst/", tip: "词尾几个辅音快速收住，不加“额”。", ex: [["six", "sɪks"], ["next", "nekst"], ["texts", "teksts"]] },
      ],
      pairs: [["sport", "spɔːt", "support", "səˈpɔːt"], ["please", "pliːz", "police", "pəˈliːs"], ["blow", "bləʊ", "below", "bɪˈləʊ"]],
      words: [
        ["tomorrow", "təˈmɒrəʊ", "明天"], ["next", "nekst", "下一个"], ["plan", "plæn", "计划"], ["travel", "ˈtrævl", "旅行"],
        ["going", "ˈɡəʊɪŋ", "打算"], ["start", "stɑːt", "开始"], ["study", "ˈstʌdi", "学习"], ["weekend", "ˌwiːkˈend", "周末"],
      ],
      phrases: [
        ["I'm going to study.", "aɪm ˈɡəʊɪŋ tə ˈstʌdi", "我打算学习"],
        ["next week", "nekst wiːk", "下周"],
        ["What are your plans?", "wɒt ɑː jɔː plænz", "你有什么计划？"],
        ["I'm going to travel.", "aɪm ˈɡəʊɪŋ tə ˈtrævl", "我要去旅行"],
        ["tomorrow morning", "təˈmɒrəʊ ˈmɔːnɪŋ", "明天早上"],
      ],
      sentences: [
        ["I'm going to study English every day.", "我打算每天学英语。"],
        ["Next week I'm going to visit my friend.", "下周我要去看我的朋友。"],
        ["What are you going to do this weekend?", "这个周末你打算做什么？"],
        ["Tomorrow I'm going to start early.", "明天我要早点开始。"],
      ],
      talk: [
        ["What are you going to do this weekend?", "这个周末你打算做什么？", "I'm going to see my friends."],
        ["What are you going to do tomorrow?", "你明天打算做什么？", "I'm going to work and study English."],
        ["Where are you going to travel next?", "你下次打算去哪里旅行？", "I'm going to travel to Japan."],
      ],
    },
    {
      title: "Asking Questions", zh: "提问与求助", focus: "单词重音",
      sounds: [
        { label: "重音在前 ●○", tip: "重音音节更响、更长、更高。", ex: [["teacher", "ˈtiːtʃə"], ["happy", "ˈhæpi"], ["morning", "ˈmɔːnɪŋ"]] },
        { label: "重音在后 ○●", tip: "第一个音节轻轻带过，重音落在后面。", ex: [["hotel", "həʊˈtel"], ["today", "təˈdeɪ"], ["again", "əˈɡen"]] },
        { label: "三个音节", tip: "找准那个最响的音节。", ex: [["family", "ˈfæməli"], ["beautiful", "ˈbjuːtɪfl"], ["computer", "kəmˈpjuːtə"]] },
      ],
      pairs: [["present (n.)", "ˈpreznt", "present (v.)", "prɪˈzent"], ["desert", "ˈdezət", "dessert", "dɪˈzɜːt"], ["object (n.)", "ˈɒbdʒɪkt", "object (v.)", "əbˈdʒekt"]],
      words: [
        ["question", "ˈkwestʃən", "问题"], ["answer", "ˈɑːnsə", "回答"], ["again", "əˈɡen", "再一次"], ["understand", "ˌʌndəˈstænd", "理解"],
        ["speak", "spiːk", "说"], ["slowly", "ˈsləʊli", "慢慢地"], ["English", "ˈɪŋɡlɪʃ", "英语"], ["mean", "miːn", "意思是"],
      ],
      phrases: [
        ["Do you understand?", "duː juː ˌʌndəˈstænd", "你明白吗？"],
        ["Can you say that again?", "kən juː seɪ ðæt əˈɡen", "能再说一遍吗？"],
        ["Please speak slowly.", "pliːz spiːk ˈsləʊli", "请说慢一点"],
        ["What does it mean?", "wɒt dʌz ɪt miːn", "这是什么意思？"],
        ["Are you sure?", "ɑː juː ʃʊə", "你确定吗？"],
      ],
      sentences: [
        ["Sorry, can you say that again?", "抱歉，能再说一遍吗？"],
        ["Could you speak more slowly, please?", "你能说慢一点吗？"],
        ["What does this word mean?", "这个词是什么意思？"],
        ["Do you speak Chinese?", "你会说中文吗？"],
      ],
      talk: [
        ["Do you speak English?", "你会说英语吗？", "Yes, a little. I'm learning."],
        ["Are you a student?", "你是学生吗？", "No, I'm not. I work."],
        ["Do you understand me?", "你听得懂我吗？", "Yes, I understand."],
      ],
    },
    {
      title: "Right Now", zh: "正在做（现在进行时）", focus: "/ŋ/ 和 /n/",
      sounds: [
        { label: "/ŋ/", tip: "舌根抬起顶住软腭，声音从鼻子出，像“昂”的尾音。结尾不要加 /ɡ/。", ex: [["sing", "sɪŋ"], ["long", "lɒŋ"], ["morning", "ˈmɔːnɪŋ"]] },
        { label: "/n/", tip: "舌尖顶住上牙龈，像“安”的尾音。", ex: [["thin", "θɪn"], ["ran", "ræn"], ["sun", "sʌn"]] },
      ],
      pairs: [["thin", "θɪn", "thing", "θɪŋ"], ["ran", "ræn", "rang", "ræŋ"], ["sin", "sɪn", "sing", "sɪŋ"]],
      words: [
        ["doing", "ˈduːɪŋ", "正在做"], ["cooking", "ˈkʊkɪŋ", "正在做饭"], ["reading", "ˈriːdɪŋ", "正在读"], ["working", "ˈwɜːkɪŋ", "正在工作"],
        ["waiting", "ˈweɪtɪŋ", "正在等"], ["eating", "ˈiːtɪŋ", "正在吃"], ["learning", "ˈlɜːnɪŋ", "正在学"], ["listening", "ˈlɪsnɪŋ", "正在听"],
      ],
      phrases: [
        ["What are you doing?", "wɒt ɑː juː ˈduːɪŋ", "你在做什么？"],
        ["I'm cooking.", "aɪm ˈkʊkɪŋ", "我在做饭"],
        ["I'm waiting for you.", "aɪm ˈweɪtɪŋ fə juː", "我在等你"],
        ["right now", "raɪt naʊ", "现在"],
        ["I'm listening.", "aɪm ˈlɪsnɪŋ", "我在听"],
      ],
      sentences: [
        ["What are you doing right now?", "你现在在做什么？"],
        ["I'm learning English with my coach.", "我正在和教练学英语。"],
        ["She's cooking dinner in the kitchen.", "她正在厨房做晚饭。"],
        ["We're waiting for the bus.", "我们在等公交车。"],
      ],
      talk: [
        ["What are you doing right now?", "你现在在做什么？", "I'm learning English."],
        ["What is your family doing now?", "你的家人现在在做什么？", "My mother is cooking."],
        ["Are you having fun?", "你玩得开心吗？", "Yes, I'm having fun."],
      ],
    },
    {
      title: "I Can, I Can't", zh: "能力（can / can't）+ 第三周复习", focus: "句子重音：实词重读，虚词轻读",
      sounds: [
        { label: "can 弱读 /kən/", tip: "肯定句里 can 轻轻带过，重音在动词上。", ex: [["I can *swim*.", "aɪ kən ˈswɪm"], ["You can *go*.", "juː kən ˈɡəʊ"], ["We can *try*.", "wiː kən ˈtraɪ"]] },
        { label: "can't 重读 /kɑːnt/", tip: "否定的 can't 要重读、拉长，别人才听得出是否定。", ex: [["I *can't* swim.", "aɪ ˈkɑːnt swɪm"], ["I *can't* come.", "aɪ ˈkɑːnt kʌm"], ["We *can't* stop.", "wiː ˈkɑːnt stɒp"]] },
        { label: "实词重读", tip: "名词、动词、形容词重读；to、the、a 轻读。", ex: [["I *want* to *go* *home*.", "aɪ ˈwɒnt tə ˈɡəʊ ˈhəʊm"], ["*Thanks* for the *help*.", "ˈθæŋks fə ðə ˈhelp"]] },
      ],
      pairs: [["I can go.", "aɪ kən ˈɡəʊ", "I can't go.", "aɪ ˈkɑːnt ɡəʊ"], ["She can drive.", "ʃiː kən ˈdraɪv", "She can't drive.", "ʃiː ˈkɑːnt draɪv"]],
      words: [
        ["swim", "swɪm", "游泳"], ["drive", "draɪv", "开车"], ["cook", "kʊk", "做饭"], ["sing", "sɪŋ", "唱歌"],
        ["dance", "dɑːns", "跳舞"], ["help", "help", "帮助"], ["try", "traɪ", "尝试"], ["well", "wel", "好地"],
      ],
      phrases: [
        ["I can swim.", "aɪ kən swɪm", "我会游泳"],
        ["I can't drive.", "aɪ kɑːnt draɪv", "我不会开车"],
        ["Can you help me?", "kən juː help miː", "你能帮我吗？"],
        ["I can try.", "aɪ kən traɪ", "我可以试试"],
        ["not very well", "nɒt ˈveri wel", "不太好"],
      ],
      sentences: [
        ["I can cook, but I can't sing.", "我会做饭，但我不会唱歌。"],
        ["Can you help me, please?", "你能帮帮我吗？"],
        ["I can speak a little English.", "我会说一点英语。"],
        ["She can drive very well.", "她车开得很好。"],
      ],
      talk: [
        ["Can you swim?", "你会游泳吗？", "Yes, I can, but not very well."],
        ["Can you cook?", "你会做饭吗？", "Yes, I can cook noodles."],
        ["What can you do well?", "你擅长做什么？", "I can play basketball well."],
      ],
    },

    // ───────────── Phase 4: Real Conversation ─────────────
    {
      title: "Work & Study", zh: "工作与学习目标", focus: "连读：辅音 + 元音",
      sounds: [
        { label: "辅音+元音 连读", tip: "前一个词的结尾辅音，直接连到下一个词的元音上。", ex: [["an apple", "ən‿ˈæpl"], ["pick it up", "ˈpɪk‿ɪt‿ʌp"], ["turn it off", "ˈtɜːn‿ɪt‿ɒf"]] },
        { label: "相同辅音只读一次", tip: "结尾和开头是同一个辅音，只读一次，稍微拉长。", ex: [["bad day", "bæd‿deɪ"], ["good day", "ɡʊd‿deɪ"], ["next time", "neks‿taɪm"]] },
      ],
      pairs: [],
      words: [
        ["university", "ˌjuːnɪˈvɜːsəti", "大学"], ["project", "ˈprɒdʒekt", "项目"], ["experience", "ɪkˈspɪəriəns", "经验"], ["learn", "lɜːn", "学习"],
        ["improve", "ɪmˈpruːv", "提高"], ["goal", "ɡəʊl", "目标"], ["skill", "skɪl", "技能"], ["practice", "ˈpræktɪs", "练习"],
      ],
      phrases: [
        ["I'm working on it.", "aɪm ˈwɜːkɪŋ‿ɒn‿ɪt", "我正在做"],
        ["a lot of work", "ə ˈlɒt‿əv wɜːk", "很多工作"],
        ["I want to improve.", "aɪ ˈwɒnt tʊ ɪmˈpruːv", "我想提高"],
        ["step by step", "ˈstep baɪ ˈstep", "一步一步"],
        ["It takes time.", "ɪt ˈteɪks taɪm", "需要时间"],
      ],
      sentences: [
        ["I want to improve my English step by step.", "我想一步一步提高我的英语。"],
        ["I'm working on a new project.", "我正在做一个新项目。"],
        ["My goal is to speak English every day.", "我的目标是每天说英语。"],
        ["It takes time, but I can do it.", "这需要时间，但我能做到。"],
      ],
      talk: [
        ["Why are you learning English?", "你为什么学英语？", "I'm learning English for my work."],
        ["What is your goal?", "你的目标是什么？", "My goal is to speak English fluently."],
        ["What's difficult for you?", "对你来说什么最难？", "Listening is difficult for me."],
      ],
    },
    {
      title: "Hobbies", zh: "爱好", focus: "弱读：to / and / of",
      sounds: [
        { label: "to → /tə/", tip: "to 在句中轻读成 /tə/。", ex: [["go to bed", "ɡəʊ tə bed"], ["I want to eat.", "aɪ wɒnt tə iːt"], ["time to go", "taɪm tə ɡəʊ"]] },
        { label: "and → /ən/", tip: "and 在句中轻读成 /ən/，几乎听不到 d。", ex: [["fish and chips", "fɪʃ ən tʃɪps"], ["you and me", "juː ən miː"], ["rice and beef", "raɪs ən biːf"]] },
        { label: "of → /əv/", tip: "of 轻读成 /əv/，和前面连起来。", ex: [["a cup of tea", "ə kʌp əv tiː"], ["a lot of people", "ə lɒt əv ˈpiːpl"], ["one of them", "wʌn əv ðəm"]] },
      ],
      pairs: [],
      words: [
        ["hobby", "ˈhɒbi", "爱好"], ["free time", "friː taɪm", "空闲时间"], ["running", "ˈrʌnɪŋ", "跑步"], ["photos", "ˈfəʊtəʊz", "照片"],
        ["guitar", "ɡɪˈtɑː", "吉他"], ["read", "riːd", "阅读"], ["enjoy", "ɪnˈdʒɔɪ", "享受"], ["often", "ˈɒfn", "经常"],
      ],
      phrases: [
        ["in my free time", "ɪn maɪ friː taɪm", "在我空闲时"],
        ["I enjoy reading.", "aɪ ɪnˈdʒɔɪ ˈriːdɪŋ", "我喜欢阅读"],
        ["a lot of fun", "ə lɒt əv fʌn", "很有趣"],
        ["How often?", "haʊ ˈɒfn", "多久一次？"],
        ["twice a week", "twaɪs ə wiːk", "一周两次"],
      ],
      sentences: [
        ["In my free time, I enjoy reading and running.", "空闲时我喜欢读书和跑步。"],
        ["I play the guitar twice a week.", "我一周弹两次吉他。"],
        ["Taking photos is a lot of fun.", "拍照很有意思。"],
        ["What do you like to do on weekends?", "你周末喜欢做什么？"],
      ],
      talk: [
        ["What do you do in your free time?", "你空闲时做什么？", "In my free time, I like to read and watch movies."],
        ["How often do you exercise?", "你多久锻炼一次？", "I go running twice a week."],
        ["Why do you like it?", "你为什么喜欢它？", "Because it makes me happy."],
      ],
    },
    {
      title: "Travel", zh: "旅行", focus: "语调：降调 ↘ 和升调 ↗",
      sounds: [
        { label: "降调 ↘", tip: "陈述句、what/where/how 问句，结尾声音往下降。", ex: [["I'm from China.", "aɪm frəm ˈtʃaɪnə ↘"], ["Where are you going?", "weər ɑː juː ˈɡəʊɪŋ ↘"], ["What's your name?", "wɒts jɔː ˈneɪm ↘"]] },
        { label: "升调 ↗", tip: "能用 yes/no 回答的问句，结尾声音往上扬。", ex: [["Are you ready?", "ɑː juː ˈredi ↗"], ["Is this your bag?", "ɪz ðɪs jɔː ˈbæɡ ↗"], ["Do you like it?", "də juː ˈlaɪk ɪt ↗"]] },
      ],
      pairs: [["You're ready.", "jɔː ˈredi ↘", "You're ready?", "jɔː ˈredi ↗"], ["It's yours.", "ɪts jɔːz ↘", "It's yours?", "ɪts jɔːz ↗"]],
      words: [
        ["airport", "ˈeəpɔːt", "机场"], ["ticket", "ˈtɪkɪt", "票"], ["passport", "ˈpɑːspɔːt", "护照"], ["hotel", "həʊˈtel", "酒店"],
        ["flight", "flaɪt", "航班"], ["trip", "trɪp", "旅程"], ["luggage", "ˈlʌɡɪdʒ", "行李"], ["holiday", "ˈhɒlədeɪ", "假期"],
      ],
      phrases: [
        ["one ticket to London", "wʌn ˈtɪkɪt tə ˈlʌndən", "一张去伦敦的票"],
        ["Where's my passport?", "weəz maɪ ˈpɑːspɔːt", "我的护照在哪？"],
        ["I have a reservation.", "aɪ hæv ə ˌrezəˈveɪʃn", "我有预订"],
        ["How long is the flight?", "haʊ lɒŋ ɪz ðə flaɪt", "飞行多长时间？"],
        ["Have a nice trip!", "hæv ə naɪs trɪp", "旅途愉快！"],
      ],
      sentences: [
        ["I have a reservation for two nights.", "我预订了两晚。"],
        ["Excuse me, where is gate twelve?", "打扰一下，12 号登机口在哪？"],
        ["How long does it take to get to the hotel?", "到酒店要多久？"],
        ["Last year I went to Thailand for a holiday.", "去年我去泰国度假了。"],
      ],
      talk: [
        ["Where did you go on your last holiday?", "你上次假期去了哪里？", "I went to Yunnan with my family."],
        ["Do you like travelling?", "你喜欢旅行吗？", "Yes, I love travelling. It's exciting."],
        ["Where do you want to go next?", "你下次想去哪里？", "I want to go to London."],
      ],
    },
    {
      title: "Health", zh: "看病与健康", focus: "缩略形式：I'm / don't / I've",
      sounds: [
        { label: "I'm / you're / he's", tip: "口语里几乎总是用缩略形式，更快更自然。", ex: [["I'm tired.", "aɪm ˈtaɪəd"], ["You're right.", "jɔː raɪt"], ["He's sick.", "hiːz sɪk"]] },
        { label: "don't / doesn't / didn't", tip: "n't 的 /t/ 很轻，几乎只是一个停顿。", ex: [["I don't know.", "aɪ dəʊnt nəʊ"], ["It doesn't hurt.", "ɪt ˈdʌznt hɜːt"], ["I didn't sleep.", "aɪ ˈdɪdnt sliːp"]] },
        { label: "I'll / I'd / I've", tip: "缩成一个音节。", ex: [["I'll call you.", "aɪl kɔːl juː"], ["I'd like that.", "aɪd laɪk ðæt"], ["I've got a cold.", "aɪv ɡɒt ə kəʊld"]] },
      ],
      pairs: [["I am", "aɪ æm", "I'm", "aɪm"], ["do not", "duː nɒt", "don't", "dəʊnt"], ["I will", "aɪ wɪl", "I'll", "aɪl"]],
      words: [
        ["headache", "ˈhedeɪk", "头疼"], ["fever", "ˈfiːvə", "发烧"], ["tired", "ˈtaɪəd", "累"], ["sick", "sɪk", "生病"],
        ["medicine", "ˈmedsn", "药"], ["doctor", "ˈdɒktə", "医生"], ["rest", "rest", "休息"], ["better", "ˈbetə", "更好"],
      ],
      phrases: [
        ["I don't feel well.", "aɪ dəʊnt fiːl wel", "我不太舒服"],
        ["I've got a headache.", "aɪv ɡɒt ə ˈhedeɪk", "我头疼"],
        ["You should rest.", "juː ʃʊd rest", "你应该休息"],
        ["I feel better.", "aɪ fiːl ˈbetə", "我感觉好多了"],
        ["Take care.", "teɪk keə", "保重"],
      ],
      sentences: [
        ["I don't feel well today.", "我今天不太舒服。"],
        ["I've got a headache and a fever.", "我头疼还发烧。"],
        ["You should see a doctor.", "你应该去看医生。"],
        ["I feel much better now, thanks.", "我现在好多了，谢谢。"],
      ],
      talk: [
        ["What's the matter?", "（医生）怎么了？", "I've got a headache."],
        ["How long have you felt like this?", "（医生）这样多久了？", "Since yesterday."],
        ["How do you feel today?", "你今天感觉怎么样？", "I feel much better, thanks."],
      ],
    },
    {
      title: "Making Plans", zh: "约朋友", focus: "连读：元音 + 元音（加 /j/ 或 /w/）",
      sounds: [
        { label: "滑出 /j/", tip: "以 /iː/ /aɪ/ /eɪ/ 结尾，后面接元音时，中间自然滑出 /j/。", ex: [["I am", "aɪ‿j‿æm"], ["see it", "siː‿j‿ɪt"], ["be over", "biː‿j‿ˈəʊvə"]] },
        { label: "滑出 /w/", tip: "以 /uː/ /əʊ/ /aʊ/ 结尾，后面接元音时，中间自然滑出 /w/。", ex: [["go out", "ɡəʊ‿w‿aʊt"], ["do it", "duː‿w‿ɪt"], ["you are", "juː‿w‿ɑː"]] },
      ],
      pairs: [],
      words: [
        ["available", "əˈveɪləbl", "有空的"], ["invite", "ɪnˈvaɪt", "邀请"], ["meet", "miːt", "见面"], ["dinner", "ˈdɪnə", "晚饭"],
        ["together", "təˈɡeðə", "一起"], ["maybe", "ˈmeɪbi", "也许"], ["call", "kɔːl", "打电话"], ["later", "ˈleɪtə", "稍后"],
      ],
      phrases: [
        ["Are you free on Friday?", "ɑː juː friː ɒn ˈfraɪdeɪ", "你周五有空吗？"],
        ["Let's go out.", "lets ɡəʊ‿w‿aʊt", "我们出去吧"],
        ["That sounds great.", "ðæt saʊndz ɡreɪt", "听起来不错"],
        ["How about seven?", "haʊ əˈbaʊt ˈsevn", "七点怎么样？"],
        ["See you then.", "siː juː ðen", "到时见"],
      ],
      sentences: [
        ["Are you free this Friday evening?", "这周五晚上你有空吗？"],
        ["Let's go out for dinner together.", "我们一起出去吃晚饭吧。"],
        ["How about seven o'clock?", "七点怎么样？"],
        ["That sounds great. See you then!", "听起来很棒，到时见！"],
      ],
      talk: [
        ["Are you free this weekend?", "这个周末你有空吗？", "Yes, I'm free on Saturday."],
        ["Do you want to have dinner together?", "想一起吃晚饭吗？", "That sounds great!"],
        ["What time is good for you?", "你几点方便？", "How about seven o'clock?"],
      ],
    },
    {
      title: "Telling a Story", zh: "讲一件事", focus: "意群停顿：长句分块说",
      sounds: [
        { label: "意群 /", tip: "长句子按意思分成小块，每块一口气说完，块与块之间稍微停一下。", ex: [["Last Sunday / I went to the park / with my friend.", ""], ["When I got home / I was very tired.", ""], ["First / we had lunch / and then / we watched a movie.", ""]] },
      ],
      pairs: [],
      words: [
        ["first", "fɜːst", "首先"], ["then", "ðen", "然后"], ["after that", "ˈɑːftə ðæt", "那之后"], ["finally", "ˈfaɪnəli", "最后"],
        ["suddenly", "ˈsʌdənli", "突然"], ["because", "bɪˈkɒz", "因为"], ["so", "səʊ", "所以"], ["story", "ˈstɔːri", "故事"],
      ],
      phrases: [
        ["First, we had lunch.", "fɜːst wiː hæd lʌntʃ", "首先我们吃了午饭"],
        ["and then", "ən ðen", "然后"],
        ["after that", "ˈɑːftə ðæt", "那之后"],
        ["because I was tired", "bɪˈkɒz aɪ wəz ˈtaɪəd", "因为我累了"],
        ["In the end", "ɪn ði end", "最后"],
      ],
      sentences: [
        ["Last Sunday, I went to the park with my friend.", "上周日我和朋友去了公园。"],
        ["First, we had lunch, and then we watched a movie.", "我们先吃了午饭，然后看了电影。"],
        ["Suddenly, it started to rain.", "突然开始下雨了。"],
        ["In the end, we went home because we were tired.", "最后我们回家了，因为我们累了。"],
      ],
      talk: [
        ["Tell me about your last weekend.", "说说你上个周末。", "Last weekend, I stayed home. First I cleaned the house, then I watched a movie."],
        ["What did you do yesterday evening?", "你昨天晚上做了什么？", "Yesterday evening I cooked dinner, and after that I read a book."],
        ["Tell me a happy memory.", "说一个快乐的回忆。", "When I was a child, I went to the beach with my family."],
      ],
    },
    {
      title: "Opinions", zh: "表达观点", focus: "英语节奏：重音之间等时",
      sounds: [
        { label: "像打鼓的节奏", tip: "英语的重音之间时间差不多，弱音要压缩。三句话的长度几乎一样！", ex: [["*Cats* *eat* *fish*.", ""], ["The *cats* will *eat* the *fish*.", ""], ["The *cats* have been *eating* the *fish*.", ""]] },
      ],
      pairs: [],
      words: [
        ["think", "θɪŋk", "认为"], ["agree", "əˈɡriː", "同意"], ["opinion", "əˈpɪnjən", "观点"], ["important", "ɪmˈpɔːtnt", "重要的"],
        ["interesting", "ˈɪntrəstɪŋ", "有趣的"], ["difficult", "ˈdɪfɪkəlt", "难的"], ["actually", "ˈæktʃuəli", "实际上"], ["idea", "aɪˈdɪə", "主意"],
      ],
      phrases: [
        ["I think so.", "aɪ ˈθɪŋk səʊ", "我也这么认为"],
        ["I don't think so.", "aɪ ˈdəʊnt θɪŋk səʊ", "我不这么认为"],
        ["I agree with you.", "aɪ əˈɡriː wɪð juː", "我同意你"],
        ["In my opinion", "ɪn maɪ əˈpɪnjən", "在我看来"],
        ["That's a good idea.", "ðæts ə ɡʊd aɪˈdɪə", "好主意"],
      ],
      sentences: [
        ["I think English is interesting, but it's difficult.", "我觉得英语很有趣，但很难。"],
        ["In my opinion, practice is the most important thing.", "在我看来，练习是最重要的。"],
        ["I agree with you.", "我同意你。"],
        ["Actually, I don't think so.", "其实，我不这么认为。"],
      ],
      talk: [
        ["Do you think English is difficult?", "你觉得英语难吗？", "I think it's difficult, but it's interesting."],
        ["Is it better to live in a city or in the countryside?", "住在城市好还是乡下好？", "In my opinion, the city is better, because there are more jobs."],
        ["What's the best way to learn English?", "学英语最好的方法是什么？", "I think speaking every day is the best way."],
      ],
    },
    {
      title: "Comparing", zh: "比较", focus: "强调重音：重读的词改变意思",
      sounds: [
        { label: "强调重音", tip: "把你想强调的词说得更响更长。听听意思怎么变。", ex: [["I like *tea*, not coffee.", ""], ["*I* like tea, not him.", ""], ["It's *my* book, not yours.", ""]] },
      ],
      pairs: [],
      words: [
        ["bigger", "ˈbɪɡə", "更大"], ["better", "ˈbetə", "更好"], ["more", "mɔː", "更多"], ["than", "ðæn", "比"],
        ["best", "best", "最好"], ["most", "məʊst", "最"], ["cheaper", "ˈtʃiːpə", "更便宜"], ["faster", "ˈfɑːstə", "更快"],
      ],
      phrases: [
        ["bigger than", "ˈbɪɡə ðən", "比……大"],
        ["much better", "mʌtʃ ˈbetə", "好得多"],
        ["the best way", "ðə best weɪ", "最好的方法"],
        ["more interesting", "mɔːr ˈɪntrəstɪŋ", "更有趣"],
        ["as good as", "əz ɡʊd əz", "和……一样好"],
      ],
      sentences: [
        ["{city} is bigger than my hometown.", "{city}比我的家乡大。"],
        ["Taking the subway is faster than driving.", "坐地铁比开车快。"],
        ["This one is cheaper, but that one is better.", "这个更便宜，但那个更好。"],
        ["Summer is my favourite season. It's the best!", "夏天是我最喜欢的季节，最棒了！"],
      ],
      talk: [
        ["Which do you like more, tea or coffee?", "茶和咖啡你更喜欢哪个？", "I like tea more than coffee."],
        ["Which is faster, the subway or the bus?", "地铁和公交哪个快？", "The subway is faster than the bus."],
        ["What's the best food in your hometown?", "你家乡最好吃的是什么？", "The best food in my hometown is hotpot."],
      ],
    },
    {
      title: "Introduce Yourself", zh: "一分钟自我介绍 · 30 天总复习", focus: "综合：/θ/ /v/ /r/ /l/",
      sounds: [
        { label: "/θ/ /ð/", tip: "舌尖放在牙齿之间。", ex: [["three", "θriː"], ["this", "ðɪs"], ["mother", "ˈmʌðə"]] },
        { label: "/v/ /w/", tip: "v 碰嘴唇，w 不碰。", ex: [["very well", "ˈveri wel"], ["we", "wiː"], ["five", "faɪv"]] },
        { label: "/r/ /l/", tip: "r 不碰上颚，l 顶住牙龈。", ex: [["right", "raɪt"], ["light", "laɪt"], ["really", "ˈrɪəli"]] },
      ],
      pairs: [["think", "θɪŋk", "sink", "sɪŋk"], ["vest", "vest", "west", "west"], ["right", "raɪt", "light", "laɪt"]],
      words: [
        ["introduce", "ˌɪntrəˈdjuːs", "介绍"], ["myself", "maɪˈself", "我自己"], ["born", "bɔːn", "出生"], ["grew up", "ɡruː ʌp", "长大"],
        ["hometown", "ˈhəʊmtaʊn", "家乡"], ["dream", "driːm", "梦想"], ["future", "ˈfjuːtʃə", "未来"], ["fluent", "ˈfluːənt", "流利的"],
      ],
      phrases: [
        ["Let me introduce myself.", "let miː ˌɪntrəˈdjuːs maɪˈself", "我来介绍一下自己"],
        ["I was born in …", "aɪ wəz bɔːn ɪn", "我出生在……"],
        ["I grew up in …", "aɪ ɡruː ʌp ɪn", "我在……长大"],
        ["My dream is to …", "maɪ driːm ɪz tə", "我的梦想是……"],
        ["I'm getting better.", "aɪm ˈɡetɪŋ ˈbetə", "我越来越好了"],
      ],
      sentences: [
        ["Let me introduce myself. My name is {name}.", "我来介绍一下，我叫{name}。"],
        ["I was born in {city}, and I grew up there.", "我出生在{city}，也在那里长大。"],
        ["I work hard, and in my free time I like music.", "我工作很努力，空闲时喜欢音乐。"],
        ["My dream is to speak English fluently.", "我的梦想是说一口流利的英语。"],
      ],
      talk: [
        ["Please introduce yourself.", "请介绍一下你自己。", "Let me introduce myself. My name is {name}. I'm from China. I work in an office. In my free time, I like reading. My dream is to speak English fluently."],
        ["What have you learned this month?", "这个月你学到了什么？", "I've learned a lot of new words and sentences."],
        ["What will you do next month?", "下个月你会做什么？", "I'm going to keep practising every day."],
      ],
    },
  ];

  const api = { PHASES, DAYS };
  root.DEC = root.DEC || {};
  root.DEC.curriculum = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
